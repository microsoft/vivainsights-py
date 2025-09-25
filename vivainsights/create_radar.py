# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
create_radar: Parameterized radar-chart workflow (calc + viz + wrapper),
in the same spirit as create_bar.

Features
- Accepts dynamic metrics, segment column, titles, figsize, etc.
- Optional indexing (Total = 100 by default). Other modes supported.
- Optional auto-segmentation via vi.identify_usage_segments if segment_col missing.
- Returns either a plot or a table.

Examples
--------
Minimal plot with default indexing against total:
>>> import vivainsights as vi
>>> pq_data = vi.load_pq_data()
>>> fig = create_radar(
...     data=pq_data,
...     metrics=["Copilot_actions_taken_in_Teams", "Collaboration_hours",
...              "After_hours_collaboration_hours", "Internal_network_size"]
... )

Return the indexed table instead of a plot:

>>> tbl = create_radar(
...     data=pq_data,
...     metrics=["Copilot_actions_taken_in_Teams", "Collaboration_hours"],
...     return_type="table"
... )

Reference a specific segment as 100 (ref_group indexing):

>>> fig = create_radar(
...     data=pq_data,
...     metrics=["Collaboration_hours", "Meetings_count"],
...     index_mode="ref_group",
...     index_ref_group="Power User"
... )

Min–max scaling to [0,100] within observed segment ranges:

>>> fig = create_radar(
...     data=pq_data,
...     metrics=["Collaboration_hours", "Meetings_count", "Focus_hours"],
...     index_mode="minmax"
... )

>>> # More complex example with auto-segmentation, custom segments, and date-range caption
... import vivainsights as vi
... pq_data = vi.load_pq_data()
... fig = create_radar(
...     data=pq_data,
...     metrics=["Copilot_actions_taken_in_Excel","Copilot_actions_taken_in_Outlook",
...                                "Copilot_actions_taken_in_Word","Copilot_actions_taken_in_Powerpoint","Copilot_actions_taken_in_Copilot_chat_(work)"],  # or selected_metrics
...     segment_col="UsageSegments_12w",
...     person_id_col="PersonId",
...     auto_segment_if_missing=True,
...     identify_metric="Copilot_actions_taken_in_Teams",
...     identify_version="4w",
...     mingroup=5,
...     agg="mean",
...     index_mode="total",  # options: "total", "none", "ref_group", "minmax"
...     index_ref_group=None,
...     dropna=False,
...     required_segments=None,  # or ["Power User", "Habitual User", "Novice User", "Low User", "Non-user"]
...     synonyms_map=None,
...     enforce_required_segments=True,
...     auto_relax_mingroup=True,
...     fill_missing_with_plot="zero",  # or "nan"
...     return_type="plot",  # or "table"
...     figsize=(8, 6),
...     title="Behavioral Profiles by Segment",
...     # subtitle="Copilot usage radar chart",
...     caption_from_date_range=True,
...     caption_text="Indexed to overall average (Total = 100)",
...     legend_loc="upper right",
...     legend_bbox_to_anchor=(1.3, 1.1),
...     alpha_fill=0.01,
...     linewidth=1.5
... )


"""

from typing import List, Optional, Tuple, Literal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    import vivainsights as vi
    from vivainsights.extract_date_range import extract_date_range
except Exception:
    vi = None
    def extract_date_range(data, return_type='text'):
        return ""

CANONICAL_ORDER = ["Power User", "Habitual User", "Novice User", "Low User", "Non-user"]
DEFAULT_SYNONYMS: Dict[str, str] = {
    # common variants → canonical
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


from matplotlib.lines import Line2D
from typing import Dict  # needed for DEFAULT_SYNONYMS annotations

# Try vivainsights highlight color; fall back to hex
try:
    from vivainsights.color_codes import Colors
    _HIGHLIGHT = Colors.HIGHLIGHT_NEGATIVE.value
except Exception:
    _HIGHLIGHT = "#fe7f4f"

# Header layout constants (match Lorenz style)
_TITLE_Y   = 0.955
_SUB_Y     = 0.915
_RULE_Y    = 0.900
_TOP_LIMIT = 0.80

def _retitle_left(fig, title_text, subtitle_text=None, left=0.01):
    """Left-aligned figure-level title/subtitle; clear any axes titles/supertitle."""
    for ax in fig.get_axes():
        try: ax.set_title("")
        except Exception: pass
    if getattr(fig, "_suptitle", None) is not None:
        fig._suptitle.set_visible(False)

    fig.text(left, _TITLE_Y, title_text or "", ha="left", fontsize=13, weight="bold", alpha=.8)
    if subtitle_text:
        fig.text(left, _SUB_Y, subtitle_text, ha="left", fontsize=11, alpha=.8)

def _add_header_decoration(fig, color=_HIGHLIGHT, y=_RULE_Y):
    """Orange rule + small box under the subtitle."""
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

def _canonicalize_segments(
    df: pd.DataFrame,
    segment_col: str,
    synonyms_map: Dict[str, str]
) -> pd.DataFrame:
    def _canon(x):
        if pd.isna(x):
            return x
        return synonyms_map.get(str(x), str(x))
    out = df.copy()
    out[segment_col] = out[segment_col].map(_canon)
    return out

def _ensure_required_segments(
    df: pd.DataFrame,
    segment_col: str,
    metrics: List[str],
    required_segments: List[str],
) -> pd.DataFrame:
    """Add missing segment rows with NaNs for metrics so they can still be shown/ordered."""
    present = set(df[segment_col].astype(str))
    missing = [s for s in required_segments if s not in present]
    if not missing:
        return df

    filler = pd.DataFrame([{segment_col: seg, **{m: np.nan for m in metrics}} for seg in missing])
    out = pd.concat([df, filler], ignore_index=True)
    return out

# =========================
# 1) CALC
# =========================
def create_radar_calc(
    data: pd.DataFrame,
    metrics: List[str],
    segment_col: str = "UsageSegments_12w",
    person_id_col: str = "PersonId",
    mingroup: int = 5,
    agg: Literal["mean","median"] = "mean",
    index_mode: Literal["total","none","ref_group","minmax"] = "total",
    index_ref_group: Optional[str] = None,
    dropna: bool = True,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Name
    ----
    create_radar_calc

    Description
    -----------
    Compute segment-level metric values and (optionally) index them for radar plotting.
    The function first aggregates at the person-within-segment level (mean/median),
    then aggregates across people to the segment level, enforces a minimum group size,
    and finally applies one of the supported indexing modes.

    Parameters
    ----------
    data : pd.DataFrame
        Source table containing `metrics`, `segment_col`, and `person_id_col`.
    metrics : List[str]
        Numeric metric column names to summarize and index for the radar chart.
    segment_col : str, default "UsageSegments_12w"
        Column identifying the segment/class for each person (e.g., usage segments).
    person_id_col : str, default "PersonId"
        Column uniquely identifying people for person-level aggregation.
    mingroup : int, default 5
        Minimum number of unique people required in a segment to retain it.
    agg : {"mean","median"}, default "mean"
        Aggregation function for both person-level and segment-level summaries.
    index_mode : {"total","none","ref_group","minmax"}, default "total"
        - "total": index each metric vs. the overall person-level average (Total=100).
        - "ref_group": index vs. a specific segment given by `index_ref_group` (Ref=100).
        - "minmax": scale to [0,100] within the min–max of observed segment values (per metric).
        - "none": return raw (unindexed) segment values.
    index_ref_group : Optional[str], default None
        Required when `index_mode="ref_group"`. Name of the segment to serve as reference (=100).
    dropna : bool, default True
        If True, drop rows with NA in any of `[person_id_col, segment_col] + metrics` prior to aggregation.

    Returns
    -------
    (segment_level_indexed, ref) : Tuple[pd.DataFrame, pd.Series]
        segment_level_indexed
            One row per segment, wide across `metrics`. Values are indexed/scaled as per `index_mode`.
        ref
            The reference used for indexing:
            - For "total" / "ref_group": a pd.Series of reference means/medians.
            - For "minmax": a two-column Series-like (MultiIndex) with per-metric min and max.
            - For "none": empty Series.

    Raises
    ------
    ValueError
        If `index_mode="ref_group"` and `index_ref_group` is missing or not found.
    KeyError
        If any of `metrics`, `segment_col`, or `person_id_col` are not present in `data`.

    Notes
    -----
    - Person-level aggregation precedes segment-level aggregation to avoid over-weighting
      individuals with more rows. This mirrors common workplace analytics practice.
    - `mingroup` is enforced using the unique person count per segment to protect privacy
      and avoid unstable small-group estimates.

    Examples
    --------
    >>> tbl, ref = create_radar_calc(
    ...     data=df,
    ...     metrics=["Collaboration_hours", "Meetings_count"],
    ...     segment_col="UsageSegments_12w",
    ...     person_id_col="PersonId",
    ...     index_mode="total"
    ... )
    """
    df = data.copy()
    if dropna:
        df = df.dropna(subset=[person_id_col, segment_col] + metrics)

    # Person-level averaging within segment
    if agg == "mean":
        person_level = (df.groupby([person_id_col, segment_col])[metrics]
                          .mean().reset_index())
    else:
        person_level = (df.groupby([person_id_col, segment_col])[metrics]
                          .median().reset_index())

    # Segment-level aggregation across people
    if agg == "mean":
        segment_level = (person_level.groupby(segment_col)[metrics]
                           .mean().reset_index())
    else:
        segment_level = (person_level.groupby(segment_col)[metrics]
                           .median().reset_index())

    # Enforce mingroup (by unique people per segment)
    counts = (person_level.groupby(segment_col)[person_id_col]
              .nunique().rename("n"))
    segment_level = segment_level.merge(counts, on=segment_col, how="left")
    segment_level = segment_level[segment_level["n"] >= mingroup].copy()
    segment_level.drop(columns=["n"], inplace=True)

    # Compute reference for indexing
    if index_mode == "total":
        ref = person_level[metrics].mean() if agg == "mean" else person_level[metrics].median()
    elif index_mode == "ref_group":
        if index_ref_group is None:
            raise ValueError("index_ref_group must be provided when index_mode='ref_group'.")
        ref_row = segment_level.loc[segment_level[segment_col] == index_ref_group]
        if ref_row.empty:
            raise ValueError(f"Reference group '{index_ref_group}' not found in {segment_col}.")
        ref = ref_row[metrics].iloc[0]
    elif index_mode == "minmax":
        mins = segment_level[metrics].min()
        maxs = segment_level[metrics].max()
        ref = pd.concat({"min": mins, "max": maxs}, axis=1)
    else:  # "none"
        ref = pd.Series(dtype=float)

    # Indexing
    segment_level_indexed = segment_level.copy()
    if index_mode in ("total", "ref_group"):
        for m in metrics:
            denom = ref[m] if (hasattr(ref, "__getitem__") and m in ref) else np.nan
            segment_level_indexed[m] = (segment_level_indexed[m] / denom) * 100.0
    elif index_mode == "minmax":
        mins = ref["min"]; maxs = ref["max"]
        for m in metrics:
            den = (maxs[m] - mins[m])
            segment_level_indexed[m] = 100.0 * (segment_level_indexed[m] - mins[m]) / (den if den != 0 else 1.0)
    # else: "none" → leave raw values

    return segment_level_indexed, ref

# =========================
# 2) VIZ
# =========================
def create_radar_viz(
    segment_level_indexed: pd.DataFrame,
    metrics: List[str],
    segment_col: str = "UsageSegments_12w",
    figsize: Tuple[float,float] = (8,6),
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    caption: Optional[str] = None,
    legend_loc: str = "upper right",
    legend_bbox_to_anchor: Tuple[float,float] = (1.3,1.1),
    alpha_fill: float = 0.10,
    linewidth: float = 1.5,
    order: Optional[List[str]] = None,
    fill_missing_with_plot: Literal["zero","nan"] = "zero",
) -> plt.Figure:
    """
    Name
    ----
    create_radar_viz

    Description
    -----------
    Render a radar (spider) chart from a wide, segment-level table produced by
    `create_radar_calc`. Each row in `segment_level_indexed` is plotted as a polygon
    across the supplied `metrics` in the given order.

    Parameters
    ----------
    segment_level_indexed : pd.DataFrame
        One row per segment, columns include `segment_col` and each of `metrics`.
        Values should already be indexed/scaled to comparable units.
    metrics : List[str]
        Ordered list of metric columns to plot around the radar.
    segment_col : str, default "UsageSegments_12w"
        Column containing the segment labels used in the legend.
    figsize : Tuple[float, float], default (8, 6)
        Matplotlib figure size in inches (width, height).
    title : Optional[str], default None
        Top title for the figure; if None, no title is set here.
    subtitle : Optional[str], default None
        Optional smaller line beneath the title (axes space).
    caption : Optional[str], default None
        Small text flush-center near the bottom of the figure (e.g., date range).
    legend_loc : str, default "upper right"
        Matplotlib legend `loc`.
    legend_bbox_to_anchor : Tuple[float, float], default (1.3, 1.1)
        Anchor for legend placement (useful for placing legend outside the plot).
    alpha_fill : float, default 0.10
        Alpha for polygon fill.
    linewidth : float, default 1.5
        Line width for polygon outlines.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The constructed matplotlib Figure.

    Notes
    -----
    - The metrics determine the angle positions clockwise from the top (π/2 offset).
    - Ensure that values are on a common scale (e.g., indexed to 100) for meaningful comparison.

    Examples
    --------
    >>> fig = create_radar_viz(
    ...     segment_level_indexed=tbl,
    ...     metrics=["Collaboration_hours", "Meetings_count", "Focus_hours"],
    ...     segment_col="UsageSegments_12w",
    ...     title="Behavioral Profiles by Segment (Indexed)"
    ... )
    """
    # Angles
    num_vars = len(metrics)
    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))

    # Determine plotting order
    segments = list(segment_level_indexed[segment_col].astype(str).unique())
    if order:
        # Keep only those in table; table may include NaN rows we added
        segments = [s for s in order if s in set(segment_level_indexed[segment_col].astype(str))]

    # Plot each segment in the chosen order
    for seg in segments:
        row = segment_level_indexed.loc[segment_level_indexed[segment_col].astype(str) == seg]
        if row.empty:
            continue
        vals = row[metrics].iloc[0].to_list()
        # For plotting only: replace NaNs with 0 if requested so the polygon renders
        if fill_missing_with_plot == "zero":
            vals = [0.0 if (pd.isna(v)) else float(v) for v in vals]
        vals += vals[:1]
        ax.plot(angles, vals, label=seg, linewidth=linewidth)
        ax.fill(angles, vals, alpha=alpha_fill)

    # Formatting
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids([a * 180 / np.pi for a in angles[:-1]], metrics)

    # Bottom caption (unchanged)
    if caption:
        fig.text(0.5, 0.01, caption, ha="center", va="center", fontsize=9)

    # Legend (unchanged)
    plt.legend(loc=legend_loc, bbox_to_anchor=legend_bbox_to_anchor)

    # Let Matplotlib tighten elements first...
    plt.tight_layout()

    # --- New: figure-level left-aligned header + orange rule/box + spacing ---
    _retitle_left(fig, title, subtitle, left=0.01)
    _add_header_decoration(fig)   # orange rule + box at _RULE_Y
    _reserve_header_space(fig)    # push axes down to avoid overlap

    return fig

# =========================
# 3) WRAPPER
# =========================
def create_radar(
    data: pd.DataFrame,
    metrics: List[str],
    # segmentation
    segment_col: str = "UsageSegments_12w",
    person_id_col: str = "PersonId",
    auto_segment_if_missing: bool = True,
    identify_metric: str = "Copilot_actions_taken_in_Teams",
    identify_version: Optional[str] = "4w",
    # calc params
    mingroup: int = 5,
    agg: Literal["mean","median"] = "mean",
    index_mode: Literal["total","none","ref_group","minmax"] = "total",
    index_ref_group: Optional[str] = None,
    dropna: bool = False,  # <- default False so Non-user with NaNs isn't dropped
    # NEW: segment controls
    required_segments: Optional[List[str]] = None,
    synonyms_map: Optional[Dict[str,str]] = None,
    enforce_required_segments: bool = True,
    auto_relax_mingroup: bool = True,
    fill_missing_with_plot: Literal["zero","nan"] = "zero",
    # output
    return_type: Literal["plot","table"] = "plot",
    # viz params
    figsize: Tuple[float,float] = (8,6),
    title: Optional[str] = "Behavioral Profiles by Segment",
    subtitle: Optional[str] = "Copilot usage radar chart",
    caption_from_date_range: bool = True,
    caption_text: Optional[str] = None,
    legend_loc: str = "upper right",
    legend_bbox_to_anchor: Tuple[float,float] = (1.3,1.1),
    alpha_fill: float = 0.10,
    linewidth: float = 1.5,
) -> object:
    """
    Name
    ----
    create_radar

    Description
    -----------
    High-level convenience wrapper to compute segment-level metrics and either:
      (a) return the indexed table (return_type="table"), or
      (b) render a radar chart (return_type="plot").

    Parameters
    ----------
    data : pd.DataFrame
        Source table containing at least `metrics`, `person_id_col`, and either
        `segment_col` or data sufficient for auto-segmentation (see below).
    metrics : List[str]
        Numeric metric columns to visualize (order determines the radar axes).
    segment_col : str, default "UsageSegments_12w"
        Segment label column. If missing and `auto_segment_if_missing=True`,
        the function will attempt to call `vi.identify_usage_segments(...)`.
    person_id_col : str, default "PersonId"
        Unique person identifier for person-level aggregation.
    auto_segment_if_missing : bool, default True
        If True and `segment_col` not found, attempt to auto-identify usage segments
        using `vivainsights.identify_usage_segments`.
    identify_metric : str, default "Copilot_actions_taken_in_Teams"
        Metric to use when auto-identifying segments via `vivainsights`.
    identify_version : Optional[str], default None
        Optional version parameter forwarded to `vi.identify_usage_segments`.
    mingroup : int, default 5
        Minimum unique person count per segment.
    agg : {"mean","median"}, default "mean"
        Aggregation function for person- and segment-level summaries.
    index_mode : {"total","none","ref_group","minmax"}, default "total"
        Indexing/scaling mode applied to segment values prior to plotting.
    index_ref_group : Optional[str], default None
        Required when `index_mode="ref_group"`. The name of the segment that will be fixed at 100.
    dropna : bool, default True
        Drop rows with NA in required columns prior to aggregation.
    return_type : {"plot","table"}, default "plot"
        - "plot": return a matplotlib Figure.
        - "table": return the indexed segment-level DataFrame.
    figsize : Tuple[float, float], default (8, 6)
        Figure size for the plot (ignored when return_type="table").
    title : Optional[str], default "Behavioral Profiles by Segment"
        Plot title. If indexing is used, a suffix "(Indexed)" is appended automatically.
    subtitle : Optional[str], default None
        Optional subtitle line below the main title.
    caption_from_date_range : bool, default True
        If True and `extract_date_range` is available, append a date-range caption
        derived from `data`.
    caption_text : Optional[str], default None
        Additional caption text. If `caption_from_date_range` also yields text,
        both are combined as "date-range | caption_text".
    legend_loc : str, default "upper right"
        Legend location (matplotlib).
    legend_bbox_to_anchor : Tuple[float, float], default (1.3, 1.1)
        Legend anchor to place legend outside the plot area.
    alpha_fill : float, default 0.10
        Polygon fill alpha.
    linewidth : float, default 1.5
        Polygon line width.

    Returns
    -------
    matplotlib.figure.Figure or pd.DataFrame
        - If `return_type="plot"`: a Figure containing the radar chart.
        - If `return_type="table"`: the segment-level indexed DataFrame.

    Raises
    ------
    ImportError
        If auto-segmentation is required (segment_col missing) but `vivainsights` is not available.
    ValueError
        If `index_mode="ref_group"` and `index_ref_group` is missing or not present in data.
    KeyError
        If required columns are missing from `data`.

    Notes
    -----
    - For meaningful radar comparisons, metrics should be on a comparable scale.
      Use "total" or "ref_group" indexing (or "minmax") when raw units differ.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> # Plot with Total=100 indexing and date-range caption
    >>> fig = create_radar(
    ...     data=pq_data,
    ...     metrics=["Copilot_actions_taken_in_Teams","Collaboration_hours",
    ...              "After_hours_collaboration_hours","Internal_network_size"],
    ...     return_type="plot",
    ... )

    >>> # Table only, no indexing
    >>> tbl = create_radar(
    ...     data=pq_data,
    ...     metrics=["Collaboration_hours","Meetings_count"],
    ...     index_mode="none",
    ...     return_type="table"
    ... )

    >>> # Ref group = 100 (e.g., "Power User")
    >>> fig = create_radar(
    ...     data=pq_data,
    ...     metrics=["Collaboration_hours","Meetings_count","Focus_hours"],
    ...     index_mode="ref_group",
    ...     index_ref_group="Power User"
    ... )

    >>> # More complex example with auto-segmentation, custom segments, and date-range caption
    ... fig = create_radar(
    ...     data=pq_data,
    ...     metrics=["Copilot_actions_taken_in_Excel","Copilot_actions_taken_in_Outlook",
    ...                                "Copilot_actions_taken_in_Word","Copilot_actions_taken_in_Powerpoint","Copilot_actions_taken_in_Copilot_chat_(work)"],  # or selected_metrics
    ...     segment_col="UsageSegments_12w",
    ...     person_id_col="PersonId",
    ...     auto_segment_if_missing=True,
    ...     identify_metric="Copilot_actions_taken_in_Teams",
    ...     identify_version="4w",
    ...     mingroup=5,
    ...     agg="mean",
    ...     index_mode="total",  # options: "total", "none", "ref_group", "minmax"
    ...     index_ref_group=None,
    ...     dropna=False,
    ...     required_segments=None,  # or ["Power User", "Habitual User", "Novice User", "Low User", "Non-user"]
    ...     synonyms_map=None,
    ...     enforce_required_segments=True,
    ...     auto_relax_mingroup=True,
    ...     fill_missing_with_plot="zero",  # or "nan"
    ...     return_type="plot",  # or "table"
    ...     figsize=(8, 6),
    ...     title="Behavioral Profiles by Segment",
    ...     # subtitle="Copilot usage radar chart",
    ...     caption_from_date_range=True,
    ...     caption_text="Indexed to overall average (Total = 100)",
    ...     legend_loc="upper right",
    ...     legend_bbox_to_anchor=(1.3, 1.1),
    ...     alpha_fill=0.01,
    ...     linewidth=1.5
    ... )
    """
    df = data.copy()
    required_segments = required_segments or CANONICAL_ORDER
    synonyms_map = synonyms_map or DEFAULT_SYNONYMS

    # Auto-identify segments if needed
    if (segment_col not in df.columns) and auto_segment_if_missing:
        if vi is None:
            raise ImportError("vivainsights not available to auto-identify usage segments.")
        df = vi.identify_usage_segments(data=df, metric=identify_metric, version=identify_version)

    # Canonicalize before calc (helps with ref_group lookups)
    df = _canonicalize_segments(df, segment_col, synonyms_map)

    # Caption
    caption = ""
    if caption_from_date_range:
        try:
            caption = extract_date_range(df, return_type='text')
        except Exception:
            caption = ""
    if caption_text:
        caption = caption_text if not caption else f"{caption} | {caption_text}"

    # Compute (first pass)
    table, ref = create_radar_calc(
        data=df,
        metrics=metrics,
        segment_col=segment_col,
        person_id_col=person_id_col,
        mingroup=mingroup,
        agg=agg,
        index_mode=index_mode,
        index_ref_group=index_ref_group,
        dropna=dropna,
    )

    # Canonicalize again (post-calc)
    table = _canonicalize_segments(table, segment_col, synonyms_map)

    # If we need specific segments and some are missing, try relaxing mingroup automatically
    have = set(table[segment_col].astype(str))
    need = set(required_segments)
    missing_first = [s for s in required_segments if s not in have]

    if enforce_required_segments and missing_first and auto_relax_mingroup and mingroup > 1:
        table_relaxed, _ = create_radar_calc(
            data=df, metrics=metrics, segment_col=segment_col,
            person_id_col=person_id_col, mingroup=1, agg=agg,
            index_mode=index_mode, index_ref_group=index_ref_group, dropna=dropna
        )
        table_relaxed = _canonicalize_segments(table_relaxed, segment_col, synonyms_map)
        # prefer relaxed results, then fall back to original where still missing
        table = table_relaxed

    # Ensure required segments rows exist (add NaN rows for truly absent)
    if enforce_required_segments:
        table = _ensure_required_segments(table, segment_col, metrics, required_segments)

    # Order rows
    cat = pd.Categorical(table[segment_col], categories=required_segments, ordered=True)
    table[segment_col] = cat
    table = table.sort_values(segment_col).reset_index(drop=True)

    if return_type == "table":
        return table

    # Title/subtitle defaults that mirror your bar style
    if index_mode in ("total","ref_group"):
        base_title = (title or "Behavioral Profiles by Segment") + " (Indexed)"
    elif index_mode == "minmax":
        base_title = (title or "Behavioral Profiles by Segment") + " (Min–Max Scaled)"
    else:
        base_title = (title or "Behavioral Profiles by Segment")

    fig = create_radar_viz(
        segment_level_indexed=table,
        metrics=metrics,
        segment_col=segment_col,
        figsize=figsize,
        title=base_title,
        subtitle=subtitle,
        caption=caption,
        legend_loc=legend_loc,
        legend_bbox_to_anchor=legend_bbox_to_anchor,
        alpha_fill=alpha_fill,
        linewidth=linewidth,
        order=required_segments,
        fill_missing_with_plot=fill_missing_with_plot,
    )
    return fig