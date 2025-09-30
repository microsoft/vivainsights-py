# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
create_survival: Parameterized Kaplan–Meier survival workflow (calc + viz + wrapper),
reusing vi.identify_usage_segments to create usage segments when needed.

Features
- Optional lifelines backend; automatic NumPy fallback if lifelines is unavailable.
- Auto-identify usage segments via vi.identify_usage_segments if `group_col` is missing.
- Required-segment ordering & synonym normalization (mirrors radar).
- Header styling: figure-left/axes-left aligned title/subtitle + orange rule/box.
- Returns either a plot or a table.

Typical call
------------
>>> import vivainsights as vi
>>> pq_data = vi.load_pq_data()
>>> fig = create_survival(
...     data=pq_data,
...     time_col="WeeksToProgress",
...     event_col="Progressed",            # 1=progressed, 0=censored
...     # If your data already has UsageSegments_12w, no auto-seg is needed.
...     # Otherwise, auto-seg will run using Copilot action metrics by default.
...     title="Time to Progression by Segment",
...     subtitle="Kaplan–Meier survival probability (remain novice)",
... )

Table output
------------
>>> tbl = create_survival(
...     data=pq_data,
...     time_col="WeeksToProgress",
...     event_col="Progressed",
...     return_type="table"
... )
"""

from typing import List, Optional, Tuple, Literal, Dict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import vivainsights as vi
# ---------- Optional dependencies ----------
try:
    from lifelines import KaplanMeierFitter  # optional; we fall back if missing
    _HAS_LIFELINES = True
except Exception:
    KaplanMeierFitter = None
    _HAS_LIFELINES = False

# ---------- vivainsights helpers ----------
try:
    from vivainsights.extract_date_range import extract_date_range
except Exception:
    vi = None
    def extract_date_range(data, return_type='text'):
        return ""

# ---------- Style / header helpers (axes-left aligned; match Lorenz/Radar) ----------
from matplotlib.lines import Line2D

try:
    from vivainsights.color_codes import Colors
    _HIGHLIGHT = Colors.HIGHLIGHT_NEGATIVE.value
except Exception:
    _HIGHLIGHT = "#fe7f4f"

_TITLE_Y   = 0.955
_SUB_Y     = 0.915
_RULE_Y    = 0.900
_TOP_LIMIT = 0.80

def _axes_left(fig) -> float:
    """Return the left x (figure coords) of the leftmost axes; fallback to 0.12."""
    axs = fig.get_axes()
    if axs:
        try:
            return float(min(ax.get_position().x0 for ax in axs))
        except Exception:
            pass
    return 0.01

def _retitle_left(fig, title_text, subtitle_text=None):
    """Figure-level title/subtitle aligned to the plotting axes' left edge."""
    for ax in fig.get_axes():
        try: ax.set_title("")
        except Exception: pass
    if getattr(fig, "_suptitle", None) is not None:
        fig._suptitle.set_visible(False)
    x = _axes_left(fig)
    fig.text(0.01, _TITLE_Y, title_text or "", ha="left", fontsize=13, weight="bold", alpha=.8)
    if subtitle_text:
        fig.text(0.01, _SUB_Y, subtitle_text, ha="left", fontsize=11, alpha=.8)

def _add_header_decoration(fig, color=_HIGHLIGHT, y=_RULE_Y):
    """Orange rule + small box, starting exactly at the axes-left anchor."""
    x_start = _axes_left(fig)
    overlay = fig.add_axes([0, 0, 1, 1], frameon=False, zorder=10)
    overlay.set_axis_off()
    overlay.add_line(Line2D([0.01, 1.0], [y, y], transform=overlay.transAxes,
                            color=color, linewidth=1.2))
    overlay.add_patch(plt.Rectangle((0.01, y), 0.03, -0.015,
                                    transform=overlay.transAxes,
                                    facecolor=color, linewidth=0))

def _reserve_header_space(fig, top=_TOP_LIMIT):
    """Push axes down so the header never overlaps."""
    try:
        if hasattr(fig, "get_constrained_layout") and fig.get_constrained_layout():
            fig.set_constrained_layout(False)
    except Exception:
        pass
    fig.subplots_adjust(top=top)

# ---------- Segment canonicalization (same approach as radar) ----------
CANONICAL_ORDER = ["Power User", "Habitual User", "Novice User", "Low User", "Non-user"]
DEFAULT_SYNONYMS: Dict[str, str] = {
    "Power Users": "Power User",
    "Power user": "Power User",
    "Habitual Users": "Habitual User",
    "Novice Users": "Novice User",
    "Novice user": "Novice User",
    "Low Users": "Low User",
    "Low users": "Low User",
    "Non-users": "Non-user",
    "Non user": "Non-user",
    "Non Users": "Non-user",
}

# Default metric set for auto-seg (present in your columns list)
DEFAULT_COPILOT_METRICS: List[str] = [
    "Copilot_actions_taken_in_Teams",
    "Copilot_actions_taken_in_Outlook",
    "Copilot_actions_taken_in_Excel",
    "Copilot_actions_taken_in_Word",
    "Copilot_actions_taken_in_Powerpoint",
]

def _canonicalize_segments(
    df: pd.DataFrame,
    segment_col: str,
    synonyms_map: Dict[str, str],
) -> pd.DataFrame:
    def _canon(x):
        if pd.isna(x):
            return x
        return synonyms_map.get(str(x), str(x))
    out = df.copy()
    if segment_col in out.columns:
        out[segment_col] = out[segment_col].map(_canon)
    return out

# ---------- Pure NumPy Kaplan–Meier (fallback if lifelines absent) ----------
def _km_numpy(durations: np.ndarray,
              events: np.ndarray,
              timeline: Optional[np.ndarray] = None) -> pd.DataFrame:
    """
    Compute unweighted KM curve with tied events handled at same time.
    durations: event/censor times (>=0), numeric
    events:   1 = event observed, 0 = censored
    timeline: optional sorted unique times; if None uses sorted unique durations
    """
    durations = np.asarray(durations, dtype=float)
    events = np.asarray(events, dtype=int)
    mask = ~np.isnan(durations) & ~np.isnan(events)
    durations, events = durations[mask], events[mask]

    if timeline is None:
        timeline = np.sort(np.unique(durations))
    else:
        timeline = np.asarray(timeline, dtype=float)

    survival, at_risk_seq, events_seq = [], [], []
    S = 1.0
    for t in timeline:
        at_risk = np.sum(durations >= t)
        d_t = np.sum((durations == t) & (events == 1))
        at_risk_seq.append(int(at_risk))
        events_seq.append(int(d_t))
        if at_risk > 0:
            S *= (1.0 - d_t / at_risk)
        survival.append(S)

    return pd.DataFrame({
        "time": timeline,
        "at_risk": at_risk_seq,
        "events": events_seq,
        "survival": survival
    })

# =========================
# 1) CALC
# =========================
def create_survival_calc(
    data: pd.DataFrame,
    time_col: str,
    event_col: str,
    group_col: Optional[str] = "UsageSegments_12w",
    id_col: Optional[str] = "PersonId",
    mingroup: int = 5,
    timeline: Optional[List[float]] = None,
    dropna: bool = True,
    use_lifelines: bool = True,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Name
    ----
    create_survival_calc

    Description
    -----------
    Compute Kaplan–Meier survival curves per segment (group).
    Uses lifelines if available (and `use_lifelines=True`), else falls back to a
    pure-NumPy implementation.

    Parameters
    ----------
    data : pd.DataFrame
        One row per subject; must include `time_col`, `event_col`, and optionally `group_col`.
    time_col : str
        Duration to event or censoring (numeric, e.g., weeks).
    event_col : str
        1 if the event occurred; 0 if censored.
    group_col : str or None, default "UsageSegments_12w"
        Segment column; if None, a single overall curve is returned.
    id_col : str or None, default "PersonId"
        Unique subject identifier (used for mingroup counting; optional).
    mingroup : int, default 5
        Minimum unique subjects required per group; groups with fewer are dropped.
    timeline : list of float, optional
        Common set of times at which to report survival. If None, per-group unique times are used.
    dropna : bool, default True
        Drop rows with NA in required columns before computing curves.
    use_lifelines : bool, default True
        If True and lifelines is available, use KaplanMeierFitter; otherwise, use NumPy fallback.

    Returns
    -------
    (survival_long, counts) : (pd.DataFrame, pd.Series)
        survival_long: long table with columns [group, time, survival, at_risk, events]
        counts:        number of unique subjects per group (after filtering)
    """
    req_cols = [time_col, event_col] + ([group_col] if group_col else [])
    for c in req_cols:
        if c and c not in data.columns:
            raise KeyError(f"Column '{c}' not found in data.")

    df = data.copy()
    if dropna:
        df = df.dropna(subset=[time_col, event_col] + ([group_col] if group_col else []))

    # counts for mingroup
    if id_col and (id_col in df.columns) and group_col:
        counts = df.groupby(group_col)[id_col].nunique()
    elif group_col:
        counts = df.groupby(group_col)[time_col].size()
    else:
        counts = pd.Series({ "Overall": len(df) })

    if group_col:
        keep_groups = counts[counts >= mingroup].index
        df = df[df[group_col].isin(keep_groups)].copy()
        counts = counts[counts.index.isin(keep_groups)]
    else:
        keep_groups = ["Overall"]

    # Build curves
    curves = []
    groups = [None] if group_col is None else sorted(df[group_col].astype(str).unique())
    for g in groups:
        sdf = df if group_col is None else df[df[group_col].astype(str) == g]
        if sdf.empty:
            continue

        durs = sdf[time_col].to_numpy(dtype=float)
        evts = sdf[event_col].to_numpy(dtype=int)
        tl = None if timeline is None else np.asarray(timeline, dtype=float)

        if use_lifelines and _HAS_LIFELINES:
            kmf = KaplanMeierFitter()
            kmf.fit(durations=durs, event_observed=evts, timeline=tl)
            out = pd.DataFrame({
                "time": kmf.survival_function_.index.values.astype(float),
                "survival": kmf.survival_function_["KM_estimate"].values.astype(float)
            })
            # lifelines event table for at_risk / events
            et = kmf.event_table.reset_index().rename(columns={"observed": "events"})
            out = out.merge(et[["event_at", "at_risk", "events"]].rename(columns={"event_at": "time"}),
                            on="time", how="left")
        else:
            out = _km_numpy(durs, evts, tl)

        out[group_col if group_col else "group"] = (g if g is not None else "Overall")
        curves.append(out)

    survival_long = pd.concat(curves, ignore_index=True) if curves else pd.DataFrame(
        columns=[group_col if group_col else "group", "time", "survival", "at_risk", "events"]
    )

    # Ensure column name for group is consistent
    if group_col is None:
        survival_long.rename(columns={"group": "group"}, inplace=True)
        grp_col = "group"
    else:
        grp_col = group_col

    # Order columns
    survival_long = survival_long[[grp_col, "time", "survival", "at_risk", "events"]]

    return survival_long, counts

# =========================
# 2) VIZ
# =========================
def create_survival_viz(
    survival_long: pd.DataFrame,
    group_col: str = "UsageSegments_12w",
    figsize: Tuple[float,float] = (8,6),
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    caption: Optional[str] = None,
    legend_loc: str = "upper right",
    legend_bbox_to_anchor: Tuple[float,float] = (1.3,1.1),
    order: Optional[List[str]] = None,
    linewidth: float = 2.0,
    missing_draw: Literal["nan","one"] = "nan",
) -> plt.Figure:
    """
    Name
    ----
    create_survival_viz

    Description
    -----------
    Render Kaplan–Meier survival step-curves for each segment in `survival_long`.
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Determine groups & time span
    groups_present = list(survival_long[group_col].astype(str).unique()) if not survival_long.empty else []
    if order:
        groups = [g for g in order if g in groups_present] + [g for g in groups_present if g not in (order or [])]
    else:
        groups = groups_present

    if survival_long.empty:
        ax.set_xlabel("Time")
        ax.set_ylabel("Survival probability")
        ax.set_ylim(0, 1)
    else:
        t_min = float(np.nanmin(survival_long["time"].values))
        t_max = float(np.nanmax(survival_long["time"].values))

        for g in groups:
            sdf = survival_long[survival_long[group_col].astype(str) == g]
            if sdf.empty:
                if missing_draw == "one":
                    ax.step([t_min, t_max], [1.0, 1.0], where="post", linewidth=linewidth, label=g, linestyle="--")
                continue
            x = sdf["time"].to_numpy(dtype=float)
            y = sdf["survival"].to_numpy(dtype=float)
            ax.step(x, y, where="post", linewidth=linewidth, label=g)

    # Formatting
    ax.set_xlabel("Time")
    ax.set_ylabel("Survival probability")
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

    # Bottom caption (optional)
    if caption:
        fig.text(0.5, 0.01, caption, ha="center", va="center", fontsize=9)

    # Legend
    plt.legend(loc=legend_loc, bbox_to_anchor=legend_bbox_to_anchor)

    # Let layout settle, then add the figure-level header + orange rule/box
    plt.tight_layout()
    _retitle_left(fig, title, subtitle)
    _add_header_decoration(fig)
    _reserve_header_space(fig)

    return fig

# =========================
# 3) WRAPPER
# =========================
def create_survival(
    data: pd.DataFrame,
    time_col: str,
    event_col: str,
    # segmentation
    group_col: Optional[str] = "UsageSegments_12w",   # expected from identify_usage_segments
    auto_segment_if_missing: bool = True,
    identify_metric: Optional[str] = None,            # single metric name OR...
    identify_metric_str: Optional[List[str]] = None,  # list of metrics to sum (default Copilot set)
    identify_version: Optional[str] = "12w",          # "12w", "4w", or None for custom thresholds
    # custom params if version=None (passed through to vi.identify_usage_segments)
    threshold: Optional[int] = None,
    width: Optional[int] = None,
    max_window: Optional[int] = None,
    power_thres: Optional[float] = None,

    id_col: Optional[str] = "PersonId",
    required_segments: Optional[List[str]] = None,
    synonyms_map: Optional[Dict[str,str]] = None,
    enforce_required_segments: bool = True,
    mingroup: int = 5,

    # calc
    timeline: Optional[List[float]] = None,
    dropna: bool = True,
    use_lifelines: bool = True,

    # output
    return_type: Literal["plot","table"] = "plot",

    # viz params
    figsize: Tuple[float,float] = (8,6),
    title: Optional[str] = "Survival Curve by Segment",
    subtitle: Optional[str] = "Kaplan–Meier estimate",
    caption_from_date_range: bool = True,
    caption_text: Optional[str] = None,
    legend_loc: str = "upper right",
    legend_bbox_to_anchor: Tuple[float,float] = (1.3,1.1),
    linewidth: float = 2.0,
    missing_draw: Literal["nan","one"] = "nan",
) -> object:
    """
    Name
    ----
    create_survival

    Description
    -----------
    High-level convenience wrapper to compute Kaplan–Meier curves and either:
      (a) return the long survival table (return_type="table"), or
      (b) render the survival plot (return_type="plot").

    Example
    -------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> fig = create_survival(
    >>> data=pq_data,                         
    >>> time_col="Active_connected_hours",
    >>> event_col="Days_of_active_Copilot_chat__work__usage",
    >>> auto_segment_if_missing=True,
    >>> identify_metric_str=[
    >>>     "Copilot_actions_taken_in_Teams",
    >>>     "Copilot_actions_taken_in_Outlook",
    >>>     "Copilot_actions_taken_in_Excel",
    >>>     "Copilot_actions_taken_in_Word",
    >>>     "Copilot_actions_taken_in_Powerpoint",
    >>> ],
    >>> identify_version="12w",
    >>> mingroup=1,                               
    >>> enforce_required_segments=True,
    >>> required_segments=["Power User","Habitual User","Novice User","Low User","Non-user"],
    >>> missing_draw="one",
    >>> )     
    """
    df = data.copy()
    synonyms_map = synonyms_map or DEFAULT_SYNONYMS
    required_segments = required_segments or CANONICAL_ORDER

    # --- Auto-identify usage segments if needed ---
    if (group_col is not None) and (group_col not in df.columns) and auto_segment_if_missing:
        if vi is None or not hasattr(vi, "identify_usage_segments"):
            raise ImportError("vivainsights.identify_usage_segments is required for auto-segmentation but is not available.")
        # default to Copilot action bundle if neither metric nor metric_str is provided
        if (identify_metric is None) and (identify_metric_str is None):
            identify_metric_str = DEFAULT_COPILOT_METRICS

        idus_kwargs = dict(
            data=df,
            metric=identify_metric,
            metric_str=identify_metric_str,
            version=identify_version,
            return_type="data"
        )
        df = vi.identify_usage_segments(**idus_kwargs)

    # Canonicalize segment labels before calc
    if group_col:
        df = _canonicalize_segments(df, group_col, synonyms_map)

    # Caption: date range if available
    caption = ""
    if caption_from_date_range:
        try:
            caption = extract_date_range(df, return_type='text')
        except Exception:
            caption = ""
    if caption_text:
        caption = caption_text if not caption else f"{caption} | {caption_text}"

    # Compute survival curves
    survival_long, counts = create_survival_calc(
        data=df,
        time_col=time_col,
        event_col=event_col,
        group_col=group_col,
        id_col=id_col,
        mingroup=mingroup,
        timeline=timeline,
        dropna=dropna,
        use_lifelines=use_lifelines,
    )

    # Canonicalize again just in case
    if group_col:
        survival_long = _canonicalize_segments(survival_long, group_col, synonyms_map)

    # If table requested, return it
    if return_type == "table":
        cols = [group_col if group_col else "group", "time", "survival", "at_risk", "events"]
        # Optional: order rows by group order if provided
        if group_col and enforce_required_segments and required_segments:
            cat = pd.Categorical(survival_long[group_col].astype(str), categories=required_segments, ordered=True)
            survival_long = survival_long.assign(**{group_col: cat}).sort_values([group_col, "time"])
        return survival_long[cols].reset_index(drop=True)

    # Title default tweak (match radar style)
    base_title = title or "Survival Curve by Segment"

    # Plot
    fig = create_survival_viz(
        survival_long=survival_long,
        group_col=(group_col if group_col else "group"),
        figsize=figsize,
        title=base_title,
        subtitle=subtitle,
        caption=caption,
        legend_loc=legend_loc,
        legend_bbox_to_anchor=legend_bbox_to_anchor,
        order=(required_segments if enforce_required_segments else None),
        linewidth=linewidth,
        missing_draw=missing_draw,
    )
    return fig