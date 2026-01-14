# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
create_radar: Parameterized radar-chart workflow (calc + viz + wrapper),
in the same spirit as create_bar.

Core design
-----------
- General-purpose: works with any segment column, not just RL12 usage segments.
- If `segment_col` is not supplied, it can automatically classify people into
  usage segments by calling `vivainsights.identify_usage_segments(...)`.
- Keeps the important calculation pipeline:
    * person-level aggregation within segment
    * segment-level aggregation
    * minimum group size (`mingroup`)
    * indexing modes: "total", "none", "ref_group", "minmax"
- Returns either a plot or a table.

Typical usage
-------------
Pre-computed segment column:

>>> import vivainsights as vi
>>> from vivainsights.create_radar import create_radar
>>>
>>> pq_data = vi.load_pq_data()
>>> fig = create_radar(
...     data=pq_data,
...     metrics=[
...         "Copilot_actions_taken_in_Teams",
...         "Collaboration_hours",
...         "After_hours_collaboration_hours",
...         "Internal_network_size",
...     ],
...     segment_col="Organization",
... )

Automatic usage segments via identify_usage_segments:

>>> # Segment people automatically into usage segments based on the same metrics
>>> fig = create_radar(
...     data=pq_data,
...     metrics=[
...         "Copilot_actions_taken_in_Excel",
...         "Copilot_actions_taken_in_Outlook",
...         "Copilot_actions_taken_in_Word",
...         "Copilot_actions_taken_in_Powerpoint",
...     ],
...     # segment_col omitted -> identify_usage_segments() is called
... )

Return the indexed table instead of a plot:

>>> tbl = create_radar(
...     data=pq_data,
...     metrics=["Collaboration_hours", "Meetings_count"],
...     segment_col="Organization",
...     return_type="table",
... )

Reference a specific segment as 100 (ref_group indexing):

>>> fig = create_radar(
...     data=pq_data,
...     metrics=["Collaboration_hours", "Meetings_count"],
...     segment_col="Organization",
...     index_mode="ref_group",
...     index_ref_group="Contoso Ltd",
... )

Min–max scaling to [0,100] within observed segment ranges:

>>> fig = create_radar(
...     data=pq_data,
...     metrics=["Collaboration_hours", "Meetings_count", "Focus_hours"],
...     segment_col="Organization",
...     index_mode="minmax",
... )
"""

from typing import List, Optional, Tuple, Literal, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from vivainsights.identify_usage_segments import identify_usage_segments
from vivainsights.extract_date_range import extract_date_range

def extract_date_range(data, return_type: str = "text") -> str:
    return ""

# Try vivainsights highlight color; fall back to hex
try:
    from vivainsights.color_codes import Colors

    _HIGHLIGHT = Colors.HIGHLIGHT_NEGATIVE.value
except Exception:
    _HIGHLIGHT = "#fe7f4f"

# Header layout constants (aligned with other visuals)
_TITLE_Y = 0.955
_SUB_Y = 0.915
_RULE_Y = 0.900
_TOP_LIMIT = 0.80

__all__ = ["create_radar_calc", "create_radar_viz", "create_radar"]


# --------------------------------------------------------------------
# Figure-level header helpers
# --------------------------------------------------------------------
def _retitle_left(fig, title_text: Optional[str], subtitle_text: Optional[str] = None, left: float = 0.01) -> None:
    """Left-aligned figure-level title/subtitle; clear any axes titles/supertitle."""
    for ax in fig.get_axes():
        try:
            ax.set_title("")
        except Exception:
            pass

    if getattr(fig, "_suptitle", None) is not None:
        fig._suptitle.set_visible(False)

    if title_text:
        fig.text(left, _TITLE_Y, title_text, ha="left", fontsize=13, weight="bold", alpha=.8)
    if subtitle_text:
        fig.text(left, _SUB_Y, subtitle_text, ha="left", fontsize=11, alpha=.8)


def _add_header_decoration(fig, color: str = _HIGHLIGHT, y: float = _RULE_Y) -> None:
    """Colored rule + small box under the subtitle."""
    overlay = fig.add_axes([0, 0, 1, 1], frameon=False, zorder=10)
    overlay.set_axis_off()
    overlay.add_line(
        Line2D([0.01, 1.0], [y, y], transform=overlay.transAxes, color=color, linewidth=1.2)
    )
    overlay.add_patch(
        plt.Rectangle(
            (0.01, y),
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


# --------------------------------------------------------------------
# 1) CALC
# --------------------------------------------------------------------
IndexMode = Literal["total", "none", "ref_group", "minmax"]


def create_radar_calc(
    data: pd.DataFrame,
    metrics: List[str],
    segment_col: str,
    person_id_col: str = "PersonId",
    mingroup: int = 5,
    agg: Literal["mean", "median"] = "mean",
    index_mode: IndexMode = "total",
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

    Steps:
      1. Aggregate to person-level within each segment (mean/median).
      2. Aggregate the person-level values to the segment level.
      3. Enforce a minimum person count per segment (`mingroup`).
      4. Apply an indexing mode to make metrics comparable.

    Parameters
    ----------
    data : pd.DataFrame
        Source table containing `metrics`, `segment_col`, and `person_id_col`.
    metrics : List[str]
        Numeric metric column names to summarise and index for the radar chart.
    segment_col : str
        Column identifying the segment/class for each person (e.g., Organization, Region, usage band).
    person_id_col : str, default "PersonId"
        Column uniquely identifying people for person-level aggregation.
    mingroup : int, default 5
        Minimum number of unique people required in a segment to retain it.
    agg : {"mean","median"}, default "mean"
        Aggregation function for both person-level and segment-level summaries.
    index_mode : {"total","none","ref_group","minmax"}, default "total"
        - "total": index each metric vs. the overall person-level average (Total = 100).
        - "ref_group": index vs. a specific segment given by `index_ref_group` (Ref = 100).
        - "minmax": scale to [0,100] within the min–max of observed segment values (per metric).
        - "none": return raw (unindexed) segment values.
    index_ref_group : Optional[str], default None
        Required when `index_mode="ref_group"`. Name of the segment to serve as reference (=100).
    dropna : bool, default True
        If True, drop rows with NA in any of `[person_id_col, segment_col] + metrics`
        prior to aggregation.

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
    """
    if not metrics:
        raise ValueError("`metrics` must be a non-empty list of column names.")

    required_cols = [person_id_col, segment_col] + metrics
    missing = [c for c in required_cols if c not in data.columns]
    if missing:
        raise KeyError(f"Missing required column(s): {missing}")

    df = data[required_cols].copy()

    if dropna:
        df = df.dropna(subset=required_cols)

    # Person-level aggregation within segment
    if agg == "mean":
        person_level = (
            df.groupby([person_id_col, segment_col])[metrics]
            .mean()
            .reset_index()
        )
    elif agg == "median":
        person_level = (
            df.groupby([person_id_col, segment_col])[metrics]
            .median()
            .reset_index()
        )
    else:
        raise ValueError("`agg` must be 'mean' or 'median'.")

    # Segment-level aggregation across people
    if agg == "mean":
        segment_level = (
            person_level.groupby(segment_col)[metrics]
            .mean()
            .reset_index()
        )
    else:
        segment_level = (
            person_level.groupby(segment_col)[metrics]
            .median()
            .reset_index()
        )

    # Enforce mingroup (by unique people per segment)
    counts = (
        person_level.groupby(segment_col)[person_id_col]
        .nunique()
        .rename("n")
    )
    segment_level = segment_level.merge(counts, on=segment_col, how="left")
    segment_level = segment_level[segment_level["n"] >= mingroup].copy()
    segment_level.drop(columns=["n"], inplace=True)

    if segment_level.empty:
        ref = pd.Series(dtype=float)
        return segment_level, ref

    # Compute reference for indexing
    if index_mode == "total":
        ref = (
            person_level[metrics].mean()
            if agg == "mean"
            else person_level[metrics].median()
        )
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
    elif index_mode == "none":
        ref = pd.Series(dtype=float)
    else:
        raise ValueError("index_mode must be one of: 'total', 'none', 'ref_group', 'minmax'.")

    # Indexing
    segment_level_indexed = segment_level.copy()
    if index_mode in ("total", "ref_group"):
        for m in metrics:
            denom = ref[m] if (hasattr(ref, "__getitem__") and m in ref) else np.nan
            segment_level_indexed[m] = (segment_level_indexed[m] / denom) * 100.0
    elif index_mode == "minmax":
        mins = ref["min"]
        maxs = ref["max"]
        for m in metrics:
            den = (maxs[m] - mins[m])
            segment_level_indexed[m] = 100.0 * (
                segment_level_indexed[m] - mins[m]
            ) / (den if den != 0 else 1.0)
    # else: "none" → leave raw values

    return segment_level_indexed, ref


# --------------------------------------------------------------------
# Auto segmentation helper
# --------------------------------------------------------------------
from pandas.api.types import is_object_dtype, is_categorical_dtype


def _auto_segment_using_identify_usage(
    data: pd.DataFrame,
    metrics: List[str],
    version: str = "12w",
) -> Tuple[pd.DataFrame, str]:
    """
    Call vivainsights.identify_usage_segments() and infer the segment column
    without hard-coding any specific segment labels.

    - If a single metric is provided, it is used as `metric=...`.
    - If multiple metrics are provided, they are passed as `metric_str=[...]`.
    - Among the newly-added columns, we look for an object/categorical column with
      a small number of distinct values, and use that as the segment column.
    """

    original_cols = set(data.columns)

    if len(metrics) == 1:
        seg_data = identify_usage_segments(
            data=data.copy(),
            metric=metrics[0],
            version=version,
            return_type="data",
        )
    else:
        seg_data = identify_usage_segments(
            data=data.copy(),
            metric_str=metrics,
            version=version,
            return_type="data",
        )

    new_cols = [c for c in seg_data.columns if c not in original_cols]
    candidates = []
    for c in new_cols:
        s = seg_data[c]
        if is_object_dtype(s) or is_categorical_dtype(s):
            nunique = s.nunique(dropna=True)
            # Usage segment columns typically have a small number of categories.
            if 1 < nunique <= 10:
                candidates.append((c, nunique))

    if not candidates:
        raise ValueError(
            "Auto usage segmentation did not produce a suitable segment column. "
            "Consider providing `segment_col` explicitly."
        )

    candidates.sort(key=lambda x: x[1])
    segment_col = candidates[0][0]
    return seg_data, segment_col


# --------------------------------------------------------------------
# 2) VIZ
# --------------------------------------------------------------------
def create_radar_viz(
    segment_level_indexed: pd.DataFrame,
    metrics: List[str],
    segment_col: str,
    figsize: Tuple[float, float] = (8, 6),
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    caption: Optional[str] = None,
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
    segment_col : str
        Column containing the segment labels used in the legend.
    figsize : Tuple[float, float], default (8, 6)
        Matplotlib figure size in inches (width, height).
    title : Optional[str], default None
        Top title for the figure.
    subtitle : Optional[str], default None
        Optional smaller line beneath the title (figure-level, not axes).
    caption : Optional[str], default None
        Small text near the bottom of the figure (e.g., date range).
    """
    if segment_level_indexed.empty:
        raise ValueError("`segment_level_indexed` is empty – nothing to plot.")

    num_vars = len(metrics)
    if num_vars == 0:
        raise ValueError("`metrics` must be a non-empty list.")

    # Angles
    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))

    segments = list(segment_level_indexed[segment_col].astype(str).unique())

    # Plot each segment
    for seg in segments:
        row = segment_level_indexed.loc[segment_level_indexed[segment_col].astype(str) == seg]
        if row.empty:
            continue

        vals = row[metrics].iloc[0].to_list()
        # Replace NaNs with 0 for plotting so the polygon renders
        vals = [0.0 if (pd.isna(v)) else float(v) for v in vals]
        vals += vals[:1]

        ax.plot(angles, vals, label=seg, linewidth=1.5)
        ax.fill(angles, vals, alpha=0.10)

    # Formatting
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids([a * 180 / np.pi for a in angles[:-1]], metrics)

    # Bottom caption
    if caption:
        fig.text(0.5, 0.01, caption, ha="center", va="center", fontsize=9)

    # Legend (simple, positioned outside on the right)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    # Let Matplotlib tighten elements first...
    plt.tight_layout()

    # Figure-level header styling
    _retitle_left(fig, title, subtitle, left=0.01)
    _add_header_decoration(fig)   # rule + box
    _reserve_header_space(fig)    # push axes down to avoid overlap

    return fig


# --------------------------------------------------------------------
# 3) WRAPPER
# --------------------------------------------------------------------
ReturnType = Literal["plot", "table"]


def create_radar(
    data: pd.DataFrame,
    metrics: List[str],
    segment_col: Optional[str] = None,
    person_id_col: str = "PersonId",
    mingroup: int = 5,
    agg: Literal["mean", "median"] = "mean",
    index_mode: IndexMode = "total",
    index_ref_group: Optional[str] = None,
    dropna: bool = False,  # often False to keep low-usage segments with NaNs
    return_type: ReturnType = "plot",
    figsize: Tuple[float, float] = (8, 6),
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    caption_from_date_range: bool = True,
    caption_text: Optional[str] = None,
    usage_version: str = "12w",
) -> Union[plt.Figure, pd.DataFrame]:
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
        Source table containing at least `metrics`, `person_id_col`, and either:
          - a pre-computed `segment_col`, or
          - enough information for `vivainsights.identify_usage_segments(...)`
            to classify people into usage segments (see `usage_version`).
    metrics : List[str]
        Numeric metric columns to visualise (order determines the radar axes).
    segment_col : Optional[str], default None
        Segment label column (e.g., Organization, Region, usage band).
        If None, the function will:
          - call `identify_usage_segments()` using `metrics` as the input metric(s), and
          - auto-detect the resulting usage-segment column.
    person_id_col : str, default "PersonId"
        Unique person identifier for person-level aggregation.
    mingroup : int, default 5
        Minimum unique person count per segment.
    agg : {"mean","median"}, default "mean"
        Aggregation function for person- and segment-level summaries.
    index_mode : {"total","none","ref_group","minmax"}, default "total"
        Indexing/scaling mode applied to segment values prior to plotting.
    index_ref_group : Optional[str], default None
        Required when `index_mode="ref_group"`. The name of the segment that will be fixed at 100.
    dropna : bool, default False
        Drop rows with NA in required columns prior to aggregation.
    return_type : {"plot","table"}, default "plot"
        - "plot": return a matplotlib Figure.
        - "table": return the indexed segment-level DataFrame.
    figsize : Tuple[float, float], default (8, 6)
        Figure size for the plot (ignored when return_type="table").
    title : Optional[str], default None
        Plot title. If None, a default title is inferred based on `index_mode`.
    subtitle : Optional[str], default None
        Optional subtitle line.
    caption_from_date_range : bool, default True
        If True and `extract_date_range` is available, append a date-range caption
        derived from `data`.
    caption_text : Optional[str], default None
        Additional caption text. If `caption_from_date_range` also yields text,
        both are combined as "date-range | caption_text".
    usage_version : str, default "12w"
        Passed through to `identify_usage_segments` when automatic segmentation
        is used (i.e., when `segment_col` is None).

    Returns
    -------
    matplotlib.figure.Figure or pd.DataFrame
        - If `return_type="plot"`: a Figure containing the radar chart.
        - If `return_type="table"`: the segment-level indexed DataFrame.
    """
    df = data.copy()

    # Automatic usage segmentation if no segment_col provided
    if segment_col is None:
        df, segment_col = _auto_segment_using_identify_usage(
            data=df,
            metrics=metrics,
            version=usage_version,
        )
    else:
        if segment_col not in df.columns:
            raise KeyError(f"segment_col '{segment_col}' not found in data.")

    # Build caption
    caption = ""
    if caption_from_date_range:
        try:
            caption = extract_date_range(df, return_type="text")
        except Exception:
            caption = ""
    if caption_text:
        caption = caption_text if not caption else f"{caption} | {caption_text}"

    # Compute segment-level table
    table, _ = create_radar_calc(
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

    if return_type == "table":
        return table

    # Default title/subtitle
    if title is None:
        base_title = "Behavioral Profiles by Segment"
        if index_mode in ("total", "ref_group"):
            base_title += " (Indexed)"
        elif index_mode == "minmax":
            base_title += " (Min–Max Scaled)"
    else:
        base_title = title

    if subtitle is None:
        subtitle_effective = f"Radar view across metrics by {segment_col}"
    else:
        subtitle_effective = subtitle

    fig = create_radar_viz(
        segment_level_indexed=table,
        metrics=metrics,
        segment_col=segment_col,
        figsize=figsize,
        title=base_title,
        subtitle=subtitle_effective,
        caption=caption,
    )
    return fig
