# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
create_survival: Parameterized Kaplan–Meier survival workflow (calc + viz + wrapper).

Design goals
------------
- General-purpose: works with any grouping column (segments, org, region, etc.).
- Optional automatic segmentation via vivainsights.identify_usage_segments, without
  hard-coding any specific segment labels.
- Uses lifelines.KaplanMeierFitter if available; falls back to a NumPy implementation.
- Reuses the figure header styling used in other vivainsights visuals.
- Returns either a plot or a table.

Example
-------------
Single overall curve (no grouping):

>>> import vivainsights as vi
>>> from vivainsights.create_survival import create_survival
>>>
>>> pq_data = vi.load_pq_data()
>>> fig = create_survival(
...     data=pq_data,
...     time_col="Active_connected_hours",
...     event_col="Days_of_active_Copilot_chat__work__usage",
... )

Pre-computed grouping column:

>>> fig = create_survival(
...     data=pq_data,
...     time_col="Active_connected_hours",
...     event_col="Days_of_active_Copilot_chat__work__usage",
...     group_col="Organization",
... )

Automatic usage segmentation via identify_usage_segments:

>>> fig = create_survival(
...     data=pq_data,
...     time_col="Active_connected_hours",
...     event_col="Days_of_active_Copilot_chat__work__usage",
...     # group_col omitted -> identify_usage_segments() is called
...     usage_metrics=[
...         "Copilot_actions_taken_in_Teams",
...         "Copilot_actions_taken_in_Outlook",
...     ],
...     usage_version="12w",
... )

Table output:

>>> tbl = create_survival(
...     data=pq_data,
...     time_col="Active_connected_hours",
...     event_col="Days_of_active_Copilot_chat__work__usage",
...     group_col="Organization",
...     return_type="table",
... )
"""

from typing import List, Optional, Tuple, Literal, Sequence, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pandas.api.types import is_object_dtype, is_categorical_dtype
from vivainsights.extract_date_range import extract_date_range
from vivainsights.color_codes import Colors
# ---------- vivainsights helpers ----------
try:
    from vivainsights.extract_date_range import extract_date_range
except Exception:  # pragma: no cover - fallback
    vi = None

    def extract_date_range(data, return_type: str = "text") -> str:
        return ""

# ---------- Style / header helpers (aligned with create_radar / Lorenz) ----------
try:
    from vivainsights.color_codes import Colors
    _HIGHLIGHT = Colors.HIGHLIGHT_NEGATIVE.value
except Exception:  # pragma: no cover - fallback
    _HIGHLIGHT = "#fe7f4f"

_TITLE_Y = 0.955
_SUB_Y = 0.915
_RULE_Y = 0.900
_TOP_LIMIT = 0.80

__all__ = ["create_survival_calc", "create_survival_viz", "create_survival"]


def _axes_left(fig) -> float:
    """Return the left x (figure coords) of the leftmost axes; fallback to 0.01."""
    axs = fig.get_axes()
    if axs:
        try:
            return float(min(ax.get_position().x0 for ax in axs))
        except Exception:
            pass
    return 0.01


def _retitle_left(fig, title_text: Optional[str], subtitle_text: Optional[str] = None) -> None:
    """Figure-level title/subtitle aligned to the plotting axes' left edge."""
    for ax in fig.get_axes():
        try:
            ax.set_title("")
        except Exception:
            pass
    if getattr(fig, "_suptitle", None) is not None:
        fig._suptitle.set_visible(False)
    x = _axes_left(fig)
    if title_text:
        fig.text(x, _TITLE_Y, title_text, ha="left", fontsize=13, weight="bold", alpha=.8)
    if subtitle_text:
        fig.text(x, _SUB_Y, subtitle_text, ha="left", fontsize=11, alpha=.8)


def _add_header_decoration(fig, color: str = _HIGHLIGHT, y: float = _RULE_Y) -> None:
    """Colored rule + small box starting approximately at the axes-left anchor."""
    x_start = _axes_left(fig)
    overlay = fig.add_axes([0, 0, 1, 1], frameon=False, zorder=10)
    overlay.set_axis_off()
    overlay.add_line(
        Line2D([x_start, 1.0], [y, y], transform=overlay.transAxes, color=color, linewidth=1.2)
    )
    overlay.add_patch(
        plt.Rectangle(
            (x_start, y),
            0.03,
            -0.015,
            transform=overlay.transAxes,
            facecolor=color,
            linewidth=0,
        )
    )


def _reserve_header_space(fig, top: float = _TOP_LIMIT) -> None:
    """Push axes down so the header never overlaps."""
    try:
        if hasattr(fig, "get_constrained_layout") and fig.get_constrained_layout():
            fig.set_constrained_layout(False)
    except Exception:
        pass
    fig.subplots_adjust(top=top)


# ---------- Pure NumPy Kaplan–Meier (fallback if lifelines absent) ----------
def _km_numpy(
    durations: np.ndarray,
    events: np.ndarray,
    timeline: Optional[np.ndarray] = None,
) -> pd.DataFrame:
    """
    Compute an unweighted Kaplan–Meier curve with tied events handled at the same time.

    Parameters
    ----------
    durations : array-like
        Event or censoring times (>=0).
    events : array-like
        1 = event observed, 0 = censored.
    timeline : array-like, optional
        Times at which to evaluate the survival function. If None, use sorted unique durations.

    Returns
    -------
    pd.DataFrame with columns ["time", "at_risk", "events", "survival"].
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

    return pd.DataFrame(
        {
            "time": timeline,
            "at_risk": at_risk_seq,
            "events": events_seq,
            "survival": survival,
        }
    )


# ---------- Auto-segmentation helper (uses identify_usage_segments) ----------
def _auto_segment_using_identify_usage(
    data: pd.DataFrame,
    usage_metrics: List[str],
    version: str = "12w",
) -> Tuple[pd.DataFrame, str]:
    """
    Call vivainsights.identify_usage_segments() and infer the segment column
    without hard-coding any specific segment names.

    - If a single metric is provided, it is used as `metric=...`.
    - If multiple metrics are provided, they are passed as `metric_str=[...]`.
    - Among the newly-added columns, we look for an object/categorical column with
      a small number of distinct values and use that as the segment column.
    """
    if vi is None or not hasattr(vi, "identify_usage_segments"):
        raise ImportError(
            "vivainsights.identify_usage_segments is required for automatic usage "
            "segmentation but is not available."
        )

    if not usage_metrics:
        raise ValueError("`usage_metrics` must be a non-empty list when using automatic segmentation.")

    original_cols = set(data.columns)

    if len(usage_metrics) == 1:
        seg_data = vi.identify_usage_segments(
            data=data.copy(),
            metric=usage_metrics[0],
            metric_str=None,
            version=version,
            return_type="data",
        )
    else:
        seg_data = vi.identify_usage_segments(
            data=data.copy(),
            metric=None,
            metric_str=usage_metrics,
            version=version,
            return_type="data",
        )

    new_cols = [c for c in seg_data.columns if c not in original_cols]
    candidates = []
    for c in new_cols:
        s = seg_data[c]
        if is_object_dtype(s) or is_categorical_dtype(s):
            nunique = s.nunique(dropna=True)
            # Usage segment-like columns usually have small cardinality
            if 1 < nunique <= 10:
                candidates.append((c, nunique))

    if not candidates:
        raise ValueError(
            "Automatic usage segmentation did not produce a suitable segment column. "
            "Consider providing `group_col` explicitly."
        )

    # Choose the column with the fewest distinct categories
    candidates.sort(key=lambda x: x[1])
    segment_col = candidates[0][0]
    return seg_data, segment_col


# =========================
# 1) CALC
# =========================
def create_survival_calc(
    data: pd.DataFrame,
    time_col: str,
    event_col: str,
    group_col: Optional[str] = None,
    id_col: Optional[str] = "PersonId",
    mingroup: int = 5,
    timeline: Optional[Sequence[float]] = None,
    dropna: bool = True,
    use_lifelines: bool = True,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Name
    ----
    create_survival_calc

    Description
    -----------
    Compute Kaplan–Meier survival curves per group (segment, org, etc.).
    Uses lifelines.KaplanMeierFitter when available (and `use_lifelines=True`),
    otherwise falls back to a simple NumPy implementation.

    Parameters
    ----------
    data : pd.DataFrame
        Input data; one row per subject (or observation) containing `time_col`,
        `event_col`, and optionally `group_col`.
    time_col : str
        Column containing durations to event or censoring (numeric, e.g., weeks).
    event_col : str
        Column with 1 if the event occurred, 0 if censored.
    group_col : str or None, default None
        Grouping column. If None, a single overall curve is returned.
    id_col : str or None, default "PersonId"
        Unique subject identifier used for `mingroup` counting. If None or not present,
        the row count per group is used instead.
    mingroup : int, default 5
        Minimum unique subjects required per group; groups with fewer are dropped.
    timeline : sequence of float, optional
        Common set of times at which to report survival. If None, per-group unique times
        are used.
    dropna : bool, default True
        Drop rows with NA in required columns before computing curves.
    use_lifelines : bool, default True
        If True and lifelines is available, use KaplanMeierFitter; otherwise, use NumPy.

    Returns
    -------
    survival_long : pd.DataFrame
        Long-format table with columns [group_col_or_"group", "time", "survival",
        "at_risk", "events"].
    counts : pd.Series
        Number of unique subjects per group (after filtering).
    """
    required = [time_col, event_col] + ([group_col] if group_col else [])
    missing = [c for c in required if (c is not None and c not in data.columns)]
    if missing:
        raise KeyError(f"Missing required column(s): {missing}")

    df = data.copy()
    if dropna:
        df = df.dropna(subset=[c for c in required if c is not None])

    # Group sizes for mingroup
    if group_col:
        if id_col and (id_col in df.columns):
            counts = df.groupby(group_col)[id_col].nunique()
        else:
            counts = df.groupby(group_col)[time_col].size()
        keep = counts[counts >= mingroup].index
        df = df[df[group_col].isin(keep)].copy()
        counts = counts[counts.index.isin(keep)]
    else:
        counts = pd.Series({"Overall": len(df)})

    # If nothing left, return empty
    if df.empty:
        col_name = group_col if group_col else "group"
        empty = pd.DataFrame(columns=[col_name, "time", "survival", "at_risk", "events"])
        return empty, counts

    # Build curves
    curves = []
    if group_col is None:
        groups = [None]
    else:
        groups = sorted(df[group_col].astype(str).unique())

    for g in groups:
        if group_col is None:
            sdf = df
        else:
            sdf = df[df[group_col].astype(str) == g]
        if sdf.empty:
            continue

        durs = sdf[time_col].to_numpy(dtype=float)
        evts = sdf[event_col].to_numpy(dtype=int)
        tl = None if timeline is None else np.asarray(timeline, dtype=float)

        if use_lifelines and _HAS_LIFELINES:
            kmf = KaplanMeierFitter()
            kmf.fit(durations=durs, event_observed=evts, timeline=tl)
            out = pd.DataFrame(
                {
                    "time": kmf.survival_function_.index.values.astype(float),
                    "survival": kmf.survival_function_["KM_estimate"].values.astype(float),
                }
            )
            et = (
                kmf.event_table.reset_index()
                .rename(columns={"observed": "events", "event_at": "time"})
            )
            out = out.merge(et[["time", "at_risk", "events"]], on="time", how="left")
        else:
            out = _km_numpy(durs, evts, tl)

        out[group_col if group_col else "group"] = g if g is not None else "Overall"
        curves.append(out)

    survival_long = pd.concat(curves, ignore_index=True)

    grp_col = group_col if group_col else "group"
    survival_long = survival_long[[grp_col, "time", "survival", "at_risk", "events"]]

    return survival_long, counts


# =========================
# 2) VIZ
# =========================
def create_survival_viz(
    survival_long: pd.DataFrame,
    group_col: str,
    figsize: Tuple[float, float] = (8, 6),
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    caption: Optional[str] = None,
    linewidth: float = 2.0,
) -> plt.Figure:
    """
    Name
    ----
    create_survival_viz

    Description
    -----------
    Render Kaplan–Meier survival step curves for each group in `survival_long`.

    Parameters
    ----------
    survival_long : pd.DataFrame
        Output of create_survival_calc, with at least [group_col, "time", "survival"].
    group_col : str
        Column name identifying the groups to plot.
    figsize : tuple of float, default (8, 6)
        Matplotlib figure size in inches (width, height).
    title : str, optional
        Figure-level title.
    subtitle : str, optional
        Smaller line beneath the title.
    caption : str, optional
        Small text near the bottom of the figure (e.g., date range).
    linewidth : float, default 2.0
        Line width for the step curves.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The constructed matplotlib Figure.
    """
    fig, ax = plt.subplots(figsize=figsize)

    if survival_long.empty:
        ax.set_xlabel("Time")
        ax.set_ylabel("Survival probability")
        ax.set_ylim(0, 1)
    else:
        groups = list(survival_long[group_col].astype(str).unique())
        for g in groups:
            sdf = survival_long[survival_long[group_col].astype(str) == g]
            if sdf.empty:
                continue
            x = sdf["time"].to_numpy(dtype=float)
            y = sdf["survival"].to_numpy(dtype=float)
            ax.step(x, y, where="post", linewidth=linewidth, label=g)

        ax.set_xlabel("Time")
        ax.set_ylabel("Survival probability")
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)

    # Caption
    if caption:
        fig.text(0.5, 0.01, caption, ha="center", va="center", fontsize=9)

    # Legend (outside on the right, similar to other vi visuals)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    # Layout + header styling
    plt.tight_layout()
    _retitle_left(fig, title, subtitle)
    _add_header_decoration(fig)
    _reserve_header_space(fig)

    return fig


# =========================
# 3) WRAPPER
# =========================
ReturnType = Literal["plot", "table"]


def create_survival(
    data: pd.DataFrame,
    time_col: str,
    event_col: str,
    group_col: Optional[str] = None,
    id_col: str = "PersonId",
    mingroup: int = 5,
    timeline: Optional[Sequence[float]] = None,
    dropna: bool = True,
    use_lifelines: bool = True,
    return_type: ReturnType = "plot",
    figsize: Tuple[float, float] = (8, 6),
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    caption_from_date_range: bool = True,
    caption_text: Optional[str] = None,
    usage_metrics: Optional[List[str]] = None,
    usage_version: str = "12w",
) -> Union[plt.Figure, pd.DataFrame]:
    """
    Name
    ----
    create_survival

    Description
    -----------
    High-level convenience wrapper to compute Kaplan–Meier curves and either:
      (a) return the long survival table (return_type="table"), or
      (b) render the survival plot (return_type="plot").

    Grouping behavior
    -----------------
    - If `group_col` is provided:
        * Curves are computed per value of that column.
    - If `group_col` is None and `usage_metrics` is provided:
        * vivainsights.identify_usage_segments() is called with `usage_metrics`,
          and the resulting usage segment column is inferred automatically.
    - If both `group_col` and `usage_metrics` are None:
        * A single overall curve is returned.

    Parameters
    ----------
    data : pd.DataFrame
        Source table containing at least `time_col`, `event_col`, and optionally
        `group_col` or metrics suitable for usage segmentation.
    time_col : str
        Duration-to-event column.
    event_col : str
        Event indicator (1 = event, 0 = censored).
    group_col : str or None, default None
        Grouping column for separate survival curves. See "Grouping behavior".
    id_col : str, default "PersonId"
        Unique subject identifier for mingroup counting.
    mingroup : int, default 5
        Minimum number of unique subjects per group.
    timeline : sequence of float, optional
        Times at which to report survival.
    dropna : bool, default True
        Drop rows with NAs in required columns prior to calculation.
    use_lifelines : bool, default True
        Use lifelines.KaplanMeierFitter when available.
    return_type : {"plot","table"}, default "plot"
        - "plot": return a matplotlib Figure.
        - "table": return the survival-long DataFrame.
    figsize : tuple of float, default (8, 6)
        Figure size in inches (only used when return_type="plot").
    title : str, optional
        Plot title. If None, a default is used.
    subtitle : str, optional
        Optional subtitle beneath the title.
    caption_from_date_range : bool, default True
        If True and extract_date_range is available, append a date-range caption.
    caption_text : str, optional
        Additional caption text. If `caption_from_date_range` also yields text,
        both are combined as "date-range | caption_text".
    usage_metrics : list of str, optional
        Metric column(s) to pass into identify_usage_segments when automatic
        usage segmentation is used (i.e., when group_col is None).
    usage_version : str, default "12w"
        Parameter forwarded to identify_usage_segments (e.g., "12w", "4w", or None).

    Returns
    -------
    matplotlib.figure.Figure or pd.DataFrame
        - If return_type="plot": a Figure containing the survival curves.
        - If return_type="table": the long survival table.
    """
    df = data.copy()
    group_col_for_calc: Optional[str] = group_col

    # Automatic usage segmentation if requested implicitly
    if group_col is None and usage_metrics:
        df, group_col_for_calc = _auto_segment_using_identify_usage(
            data=df,
            usage_metrics=usage_metrics,
            version=usage_version,
        )
    elif group_col is not None and group_col not in df.columns:
        raise KeyError(f"group_col '{group_col}' not found in data.")

    # Build caption
    caption = ""
    if caption_from_date_range:
        try:
            caption = extract_date_range(df, return_type="text")
        except Exception:
            caption = ""
    if caption_text:
        caption = caption_text if not caption else f"{caption} | {caption_text}"

    # Compute survival curves
    survival_long, counts = create_survival_calc(
        data=df,
        time_col=time_col,
        event_col=event_col,
        group_col=group_col_for_calc,
        id_col=id_col,
        mingroup=mingroup,
        timeline=timeline,
        dropna=dropna,
        use_lifelines=use_lifelines,
    )

    if return_type == "table":
        return survival_long.reset_index(drop=True)

    # Titles
    if title is None:
        if group_col_for_calc is None:
            base_title = "Survival Curve"
        else:
            base_title = "Survival Curve by Group"
    else:
        base_title = title

    if subtitle is None:
        if group_col_for_calc is None:
            subtitle_effective = "Kaplan–Meier estimate"
        else:
            subtitle_effective = f"Kaplan–Meier estimate by {group_col_for_calc}"
    else:
        subtitle_effective = subtitle

    group_col_for_viz = group_col_for_calc if group_col_for_calc is not None else "group"

    fig = create_survival_viz(
        survival_long=survival_long,
        group_col=group_col_for_viz,
        figsize=figsize,
        title=base_title,
        subtitle=subtitle_effective,
        caption=caption,
    )
    return fig
