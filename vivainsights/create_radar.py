# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
create_radar: Parameterized radar-chart workflow (calc + viz + wrapper),
in the same spirit as create_bar.

Core design
-----------
- General-purpose: works with any HR attribute column, not just RL12 usage segments.
- If `hrvar` is not supplied, it can automatically classify people into usage segments
  by calling `vivainsights.identify_usage_segments(...)`.
- Calculation pipeline:
    * person-level aggregation within each group
    * group-level aggregation
    * minimum group size (`mingroup`)
    * indexing modes: "total", "none", "ref_group", "minmax"
- Returns either a plot or a table.

Typical usage
-------------
Pre-computed HR attribute column:

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
...     hrvar="Organization",
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
...     hrvar=None,  # -> identify_usage_segments() is called
... )

Return the indexed table instead of a plot:

>>> tbl = create_radar(
...     data=pq_data,
...     metrics=["Collaboration_hours", "Meetings_count"],
...     hrvar="Organization",
...     return_type="table",
... )

Reference a specific group as 100 (ref_group indexing):

>>> fig = create_radar(
...     data=pq_data,
...     metrics=["Collaboration_hours", "Meetings_count"],
...     hrvar="Organization",
...     index_mode="ref_group",
...     index_ref_group="Contoso Ltd",
... )

Min-max scaling to [0,100] within observed group ranges:

>>> fig = create_radar(
...     data=pq_data,
...     metrics=["Collaboration_hours", "Meetings_count", "Focus_hours"],
...     hrvar="Organization",
...     index_mode="minmax",
... )
"""

from typing import List, Optional, Tuple, Literal, Union
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pandas.api.types import is_object_dtype
from vivainsights.identify_usage_segments import identify_usage_segments
from vivainsights.extract_date_range import extract_date_range
from vivainsights.us_to_space import us_to_space

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
# Auto segmentation helper
# --------------------------------------------------------------------
def _auto_segment_using_identify_usage(
    data: pd.DataFrame,
    metrics: List[str],
    version: str = "12w",
) -> Tuple[pd.DataFrame, str]:
    """
    Call vivainsights.identify_usage_segments() and infer the segment column
    without hard-coding any specific segment labels.

    - If a single metric is provided, it is used as ``metric=...``.
    - If multiple metrics are provided, they are passed as ``metric_str=[...]``.
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
        if is_object_dtype(s) or isinstance(s.dtype, pd.CategoricalDtype):
            nunique = s.nunique(dropna=True)
            # Usage segment columns typically have a small number of categories.
            if 1 < nunique <= 10:
                candidates.append((c, nunique))

    if not candidates:
        raise ValueError(
            "Auto usage segmentation did not produce a suitable segment column. "
            "Consider providing `hrvar` explicitly."
        )

    candidates.sort(key=lambda x: x[1])
    hrvar = candidates[0][0]
    return seg_data, hrvar


# --------------------------------------------------------------------
# 1) CALC
# --------------------------------------------------------------------
IndexMode = Literal["total", "none", "ref_group", "minmax"]


def create_radar_calc(
    data: pd.DataFrame,
    metrics: List[str],
    hrvar: str,
    id_col: str = "PersonId",
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
    Compute group-level metric values and (optionally) index them for radar plotting.

    Steps:
      1. Aggregate to person-level within each group (mean/median).
      2. Aggregate the person-level values to the group level.
      3. Enforce a minimum person count per group (`mingroup`).
      4. Apply an indexing mode to make metrics comparable.

    Parameters
    ----------
    data : pd.DataFrame
        Standard Person Query data frame containing `metrics`, `hrvar`, and `id_col`.
    metrics : List[str]
        Numeric metric column names to summarise and index for the radar chart.
    hrvar : str
        HR attribute column identifying the group for each person
        (e.g., "Organization", "LevelDesignation").
    id_col : str, default "PersonId"
        Column uniquely identifying people for person-level aggregation.
    mingroup : int, default 5
        Minimum number of unique people required in a group to retain it.
    agg : {"mean","median"}, default "mean"
        Aggregation function for both person-level and group-level summaries.
    index_mode : {"total","none","ref_group","minmax"}, default "total"
        - "total": index each metric vs. the overall person-level average (Total = 100).
        - "ref_group": index vs. a specific group given by `index_ref_group` (Ref = 100).
        - "minmax": scale to [0,100] within the min-max of observed group values (per metric).
        - "none": return raw (unindexed) group values.
    index_ref_group : Optional[str], default None
        Required when `index_mode="ref_group"`. Name of the group to serve as reference (=100).
    dropna : bool, default True
        If True, drop rows with NA in any of `[id_col, hrvar] + metrics` prior to aggregation.

    Returns
    -------
    (group_level_indexed, ref) : Tuple[pd.DataFrame, pd.Series]
        group_level_indexed
            One row per group, wide across `metrics`. Values are indexed/scaled as per
            `index_mode`.
        ref
            The reference used for indexing:
            - For "total" / "ref_group": a pd.Series of reference means/medians.
            - For "minmax": a two-column DataFrame with per-metric min and max.
            - For "none": empty Series.
    """
    if not metrics:
        raise ValueError("`metrics` must be a non-empty list of column names.")

    required_cols = [id_col, hrvar] + metrics
    missing = [c for c in required_cols if c not in data.columns]
    if missing:
        raise KeyError(f"Missing required column(s): {missing}")

    df = data[required_cols].copy()

    if dropna:
        df = df.dropna(subset=required_cols)

    # Person-level aggregation within group
    if agg == "mean":
        person_level = (
            df.groupby([id_col, hrvar])[metrics]
            .mean()
            .reset_index()
        )
    elif agg == "median":
        person_level = (
            df.groupby([id_col, hrvar])[metrics]
            .median()
            .reset_index()
        )
    else:
        raise ValueError("`agg` must be 'mean' or 'median'.")

    # Group-level aggregation across people
    if agg == "mean":
        group_level = (
            person_level.groupby(hrvar)[metrics]
            .mean()
            .reset_index()
        )
    else:
        group_level = (
            person_level.groupby(hrvar)[metrics]
            .median()
            .reset_index()
        )

    # Enforce mingroup (by unique people per group)
    counts = (
        person_level.groupby(hrvar)[id_col]
        .nunique()
        .rename("n")
    )
    group_level = group_level.merge(counts, on=hrvar, how="left")
    group_level = group_level[group_level["n"] >= mingroup].copy()
    group_level.drop(columns=["n"], inplace=True)

    if group_level.empty:
        ref = pd.Series(dtype=float)
        return group_level, ref

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
        ref_row = group_level.loc[group_level[hrvar] == index_ref_group]
        if ref_row.empty:
            raise ValueError(f"Reference group '{index_ref_group}' not found in {hrvar}.")
        ref = ref_row[metrics].iloc[0]
    elif index_mode == "minmax":
        mins = group_level[metrics].min()
        maxs = group_level[metrics].max()
        ref = pd.concat({"min": mins, "max": maxs}, axis=1)
    elif index_mode == "none":
        ref = pd.Series(dtype=float)
    else:
        raise ValueError("index_mode must be one of: 'total', 'none', 'ref_group', 'minmax'.")

    # Indexing
    group_level_indexed = group_level.copy()
    if index_mode in ("total", "ref_group"):
        for m in metrics:
            denom = ref[m] if (hasattr(ref, "__getitem__") and m in ref) else np.nan
            if pd.isna(denom) or denom == 0:
                warnings.warn(
                    f"Reference value for metric '{m}' is {denom}; "
                    "indexed values will be NaN for this metric.",
                    RuntimeWarning,
                    stacklevel=3,
                )
                denom = np.nan
            group_level_indexed[m] = (group_level_indexed[m] / denom) * 100.0
    elif index_mode == "minmax":
        mins = ref["min"]
        maxs = ref["max"]
        for m in metrics:
            den = (maxs[m] - mins[m])
            group_level_indexed[m] = 100.0 * (
                group_level_indexed[m] - mins[m]
            ) / (den if den != 0 else 1.0)
    # else: "none" -> leave raw values

    return group_level_indexed, ref


# --------------------------------------------------------------------
# 2) VIZ
# --------------------------------------------------------------------
def create_radar_viz(
    data: pd.DataFrame,
    metrics: List[str],
    hrvar: str,
    fill_missing: str = "zero",
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
    Render a radar (spider) chart from a wide, group-level table produced by
    `create_radar_calc`. Each row in `data` is plotted as a polygon across the
    supplied `metrics` in the given order.

    Parameters
    ----------
    data : pd.DataFrame
        One row per group, columns include `hrvar` and each of `metrics`.
        Values should already be indexed/scaled to comparable units (i.e. the
        output of `create_radar_calc`).
    metrics : List[str]
        Ordered list of metric columns to plot around the radar.
    hrvar : str
        Column containing the group labels used in the legend.
    fill_missing : str, default "zero"
        How to handle NA values in `data` before plotting:
        - "zero": replace NA with 0 so polygons close correctly.
        - "none": leave NA as-is (polygon may not render for that group).
    figsize : Tuple[float, float], default (8, 6)
        Matplotlib figure size in inches (width, height).
    title : Optional[str], default None
        Top title for the figure.
    subtitle : Optional[str], default None
        Optional smaller line beneath the title (figure-level, not axes).
    caption : Optional[str], default None
        Small text near the bottom of the figure (e.g., date range).

    Returns
    -------
    fig : matplotlib.figure.Figure
        The constructed matplotlib Figure.
    """
    if data.empty:
        raise ValueError("`data` is empty - nothing to plot.")

    if fill_missing not in ("zero", "none"):
        raise ValueError(f"`fill_missing` must be 'zero' or 'none', got {fill_missing!r}.")

    num_vars = len(metrics)
    if num_vars == 0:
        raise ValueError("`metrics` must be a non-empty list.")

    # Angles
    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))

    groups = list(data[hrvar].astype(str).unique())

    # Plot each group
    for grp in groups:
        row = data.loc[data[hrvar].astype(str) == grp]
        if row.empty:
            continue

        vals = row[metrics].iloc[0].to_list()
        if fill_missing == "zero":
            vals = [0.0 if pd.isna(v) else float(v) for v in vals]
        else:  # "none" — keep missing as NaN so the polygon renders honestly
            vals = [np.nan if pd.isna(v) else float(v) for v in vals]
        vals += vals[:1]

        ax.plot(angles, vals, label=grp, linewidth=1.5)
        ax.fill(angles, vals, alpha=0.10)

    # Formatting
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    axis_labels = [us_to_space(m) for m in metrics]
    ax.set_thetagrids([a * 180 / np.pi for a in angles[:-1]], axis_labels)

    # Bottom caption (left-aligned, matching the title anchor)
    if caption:
        fig.text(0.01, 0.01, caption, ha="left", va="center", fontsize=9)

    # Legend (outside on the right) — only when labeled artists exist
    if ax.get_legend_handles_labels()[0]:
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
    hrvar: Optional[str] = "Organization",
    id_col: str = "PersonId",
    mingroup: int = 5,
    agg: Literal["mean", "median"] = "mean",
    index_mode: IndexMode = "total",
    index_ref_group: Optional[str] = None,
    dropna: bool = False,
    return_type: ReturnType = "plot",
    figsize: Tuple[float, float] = (8, 6),
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    caption: Optional[str] = None,
    usage_version: str = "12w",
) -> Union[plt.Figure, pd.DataFrame]:
    """
    Name
    ----
    create_radar

    Description
    -----------
    High-level convenience wrapper to compute group-level metrics and either:
      (a) return the indexed table (return_type="table"), or
      (b) render a radar chart (return_type="plot").

    Parameters
    ----------
    data : pd.DataFrame
        Standard Person Query data frame containing at least `metrics`, `id_col`, and
        either a pre-computed `hrvar` column or enough information for
        `vivainsights.identify_usage_segments(...)` to classify people into usage
        segments (see `usage_version`).
    metrics : List[str]
        Numeric metric columns to visualise (order determines the radar axes).
    hrvar : Optional[str], default "Organization"
        HR attribute column used for grouping (e.g., "Organization", "LevelDesignation").
        If None, the function will:
          - call `identify_usage_segments()` using `metrics` as the input metric(s), and
          - auto-detect the resulting usage-segment column.
    id_col : str, default "PersonId"
        Unique person identifier for person-level aggregation.
    mingroup : int, default 5
        Minimum unique person count per group.
    agg : {"mean","median"}, default "mean"
        Aggregation function for person- and group-level summaries.
    index_mode : {"total","none","ref_group","minmax"}, default "total"
        Indexing/scaling mode applied to group values prior to plotting.
    index_ref_group : Optional[str], default None
        Required when `index_mode="ref_group"`. The name of the group that will be
        fixed at 100.
    dropna : bool, default False
        Drop rows with NA in required columns prior to aggregation.
    return_type : {"plot","table"}, default "plot"
        - "plot": return a matplotlib Figure.
        - "table": return the indexed group-level DataFrame.
    figsize : Tuple[float, float], default (8, 6)
        Figure size for the plot (ignored when return_type="table").
    title : Optional[str], default None
        Plot title. If None, a default title is inferred based on `index_mode`.
    subtitle : Optional[str], default None
        Optional subtitle line.
    caption : Optional[str], default None
        Additional caption text appended after the auto-generated date range and
        index label, e.g. "caption" → "Data from … | Index: … | caption".
        If None, only the date range and index label are shown.
    usage_version : str, default "12w"
        Passed through to `identify_usage_segments` when automatic segmentation
        is used (i.e., when `hrvar` is None).

    Returns
    -------
    matplotlib.figure.Figure or pd.DataFrame
        - If `return_type="plot"`: a Figure containing the radar chart.
        - If `return_type="table"`: the group-level indexed DataFrame.
    """
    df = data.copy()

    # Automatic usage segmentation if no hrvar provided
    if hrvar is None:
        df, hrvar = _auto_segment_using_identify_usage(
            data=df,
            metrics=metrics,
            version=usage_version,
        )
    else:
        if hrvar not in df.columns:
            raise KeyError(f"hrvar '{hrvar}' not found in data.")

    # Index method label (mirrors R: index_label in create_radar)
    _index_labels = {
        "total":     "Index: population average = 100",
        "minmax":    "Index: min-max scaled [0, 100]",
        "none":      "Raw values (no indexing)",
    }
    if index_mode == "ref_group":
        ref_name = index_ref_group or ""
        index_label = f"Index: {ref_name} = 100"
    else:
        index_label = _index_labels.get(index_mode, "")

    # Build caption: "<date range> | <index label>" (always auto-generated)
    auto_caption = ""
    try:
        auto_caption = extract_date_range(df, return_type="text")
    except Exception:
        pass
    auto_caption = f"{auto_caption} | {index_label}" if auto_caption else index_label
    # Append any user-supplied extra text
    caption_final = f"{auto_caption} | {caption}" if caption else auto_caption

    # Compute group-level table
    table, _ = create_radar_calc(
        data=df,
        metrics=metrics,
        hrvar=hrvar,
        id_col=id_col,
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
        base_title = "Behavioral Profiles by Group"
        if index_mode in ("total", "ref_group"):
            base_title += " (Indexed)"
        elif index_mode == "minmax":
            base_title += " (Min-Max Scaled)"
    else:
        base_title = title

    if subtitle is None:
        subtitle_effective = f"Radar view across metrics by {hrvar}"
    else:
        subtitle_effective = subtitle

    fig = create_radar_viz(
        data=table,
        metrics=metrics,
        hrvar=hrvar,
        figsize=figsize,
        title=base_title,
        subtitle=subtitle_effective,
        caption=caption_final,
    )
    return fig
