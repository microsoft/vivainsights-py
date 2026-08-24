# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Segment employees into usage-based groups from collaboration metrics.
"""

__all__ = ['identify_usage_segments', 'plot_ts_us']

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from vivainsights.identify_habit import identify_habit


def identify_usage_segments(data, metric=None, metric_str=None, version="12w", return_type="data", 
                          threshold=None, width=None, max_window=None, power_thres=None):
    """Segment employees into usage-based groups.

    Classifies each person-week as a Power User, Habitual User, Novice
    User, Low User, or Non-user, based on a rolling weekly average of the
    target metric and a habit rule counting how many weeks in the rolling
    window had any activity.  A week counts as an active (qualifying)
    week when ``target_metric >= 1``.

    **Segment definitions (12-week version)**

    Conditions are evaluated in order, and the first match wins:

    1. **Power User** - had an action in at least 9 of the trailing 12
       weeks *and* a rolling 12-week weekly average of 15 or more actions.
    2. **Habitual User** - had an action in at least 9 of the trailing 12
       weeks, but below the Power User volume threshold.
    3. **Novice User** - rolling 12-week weekly average of at least 1,
       without meeting the habit rule.
    4. **Low User** - some action in the rolling period, but a rolling
       weekly average below 1, without meeting the habit rule.
    5. **Non-user** - no actions at all in the rolling period.

    **Segment definitions (4-week version)**

    Identical in structure, but the rolling window is 4 weeks and the
    habit rule requires an action in all 4 of the trailing 4 weeks:

    1. **Power User** - an action in 4 of the trailing 4 weeks and a
       rolling 4-week weekly average of 15 or more actions.
    2. **Habitual User** - an action in 4 of the trailing 4 weeks, below
       the Power User volume threshold.
    3. **Novice User** - rolling 4-week weekly average of at least 1,
       without meeting the habit rule.
    4. **Low User** - some action in the rolling period, but a rolling
       weekly average below 1, without meeting the habit rule.
    5. **Non-user** - no actions in the rolling period.

    Because Power User is evaluated first and requires the habit rule to
    be met, Power Users are a high-volume subset of habitual users; the
    "Habitual User" label therefore only covers habitual users who fall
    below the power threshold.

    **Incomplete histories**

    Rolling averages are computed with ``min_periods=1``, so a person with
    fewer weeks of data than the window still receives an average based on
    the weeks available.  The habit rule, by contrast, always requires the
    configured number of qualifying weeks (9 of 12, or 4 of 4).  Early
    weeks in a panel and recent entrants can therefore be classified as
    Novice or Low Users even when their observed activity is high, simply
    because there is not yet enough history to satisfy the habit rule.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.  Must include ``PersonId`` and ``MetricDate``.
    metric : str or None, default None
        Single metric column to classify.
    metric_str : list of str or None, default None
        Multiple metric columns to aggregate before classification.
        Provide exactly one of *metric* or *metric_str*.
    version : str or None, default "12w"
        ``"12w"`` for 12-week rolling, ``"4w"`` for 4-week rolling, or
        ``None`` for custom parameters.  Note that when *return_type* is
        ``"data"`` both the 12-week and 4-week segments are returned
        regardless of *version*; *version* selects which column is used
        for ``"plot"`` and ``"table"``.
    return_type : str, default "data"
        ``"data"`` for a classified DataFrame, ``"plot"`` for a stacked
        bar chart, or ``"table"`` for a summary pivot table.
    threshold : int or None, default None
        Minimum value of the metric for a week to count as a qualifying
        week (required when ``version=None``).  The presets use ``1``.
    width : int or None, default None
        Number of qualifying weeks required within the window for the
        habit rule (required when ``version=None``).  The presets use
        ``9`` (12-week) and ``4`` (4-week).
    max_window : int or None, default None
        Number of weeks in the rolling window (required when
        ``version=None``).  The presets use ``12`` and ``4``.
    power_thres : float or None, default None
        Rolling weekly average at or above which a habitual user is
        classified as a Power User.  Required when ``version=None``.  For
        the ``"12w"`` and ``"4w"`` presets this is optional and defaults
        to ``15``; supplying a value overrides the preset threshold for
        both ``UsageSegments_12w`` and ``UsageSegments_4w``.

    Returns
    -------
    pandas.DataFrame or matplotlib.figure.Figure
        The output depends on *return_type*:

        - ``"data"``: the input DataFrame with additional columns.  For
          the presets these are ``target_metric``, ``target_metric_l12w``,
          ``target_metric_l4w`` (rolling weekly averages), ``IsHabit12w``
          and ``IsHabit4w`` (booleans for the habit rule), and
          ``UsageSegments_12w`` and ``UsageSegments_4w`` (the segment
          labels).  When ``version=None`` the columns are
          ``target_metric``, ``target_metric_l{max_window}w``,
          ``IsHabitCustom``, and ``UsageSegments``.
        - ``"plot"``: a stacked bar chart of the proportion of users in
          each segment over time.
        - ``"table"``: a pivot table with one row per ``MetricDate`` and
          one column per segment (``Non-user``, ``Low User``,
          ``Novice User``, ``Habitual User``, ``Power User``), where the
          values are counts of distinct ``PersonId`` values.

    Examples
    --------
    Classify usage segments using the 12-week preset:

    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.identify_usage_segments(pq_data, metric="Emails_sent", version="12w")

    Return a stacked bar chart:

    >>> vi.identify_usage_segments(pq_data, metric="Emails_sent", version="12w", return_type="plot")

    Return a summary table:

    >>> vi.identify_usage_segments(pq_data, metric="Emails_sent", version="12w", return_type="table")

    Use a metric string instead of a column name:

    >>> vi.identify_usage_segments(pq_data, metric_str="Emails_sent", version="4w")

    Select the relevant segment column after classification:

    >>> out = vi.identify_usage_segments(pq_data, metric="Emails_sent", version="12w")
    >>> out[["PersonId", "MetricDate", "UsageSegments_12w"]].head()

    Override the power user threshold on a preset:

    >>> vi.identify_usage_segments(pq_data, metric="Emails_sent", version="12w", power_thres=20)
    """
    if metric is None and metric_str is None:
        raise ValueError("Please provide either a metric or a metric_str.")
    if metric is not None and metric_str is not None:
        raise ValueError("Please provide either a metric or a metric_str, not both.")
    
    # Validate version and custom parameters
    if version is None:
        if any(param is None for param in [threshold, width, max_window, power_thres]):
            raise ValueError("When version=None, all of threshold, width, max_window, and power_thres must be provided.")
    elif version not in ["12w", "4w"]:
        raise ValueError("version must be '12w', '4w', or None.")
    
    # Validate return_type
    if return_type not in ["data", "plot", "table"]:
        raise ValueError("return_type must be 'data', 'plot', or 'table'.")

    # Prepare the target metric
    if metric is not None:
        data["target_metric"] = data[metric]
    else:
        data["target_metric"] = data[metric_str].sum(axis=1, skipna=True)

    # Create rolling averages based on version or custom parameters
    data = data.sort_values(by=["PersonId", "MetricDate"])
    
    if version is None:
        # Custom parameters provided
        # Create rolling average based on max_window
        data[f"target_metric_l{max_window}w"] = data.groupby("PersonId")["target_metric"].transform(
            lambda x: x.rolling(window=max_window, min_periods=1).mean()
        )
        
        # Print diagnostic message
        print(f"Usage segments generated with custom parameters:")
        print(f"  - threshold: {threshold}")
        print(f"  - width: {width}")
        print(f"  - max_window: {max_window}")
        print(f"  - power_thres: {power_thres}")
        
        # Identify habit with custom parameters
        habit_custom = identify_habit(data, metric="target_metric", threshold=threshold, width=width, max_window=max_window, return_type="data")
        habit_custom = habit_custom.rename(columns={"IsHabit": "IsHabitCustom"})[["PersonId", "MetricDate", "IsHabitCustom"]]
        
        # Merge habit back into the main dataset
        data = data.merge(habit_custom, on=["PersonId", "MetricDate"], how="left")
        
        # Define custom usage segments
        data["UsageSegments"] = np.select(
            [
                (data["IsHabitCustom"] == True) & (data[f"target_metric_l{max_window}w"] >= power_thres),
                (data["IsHabitCustom"] == True),
                (data[f"target_metric_l{max_window}w"] >= 1),
                (data[f"target_metric_l{max_window}w"] > 0),
                (data[f"target_metric_l{max_window}w"] == 0),
            ],
            ["Power User", "Habitual User", "Novice User", "Low User", "Non-user"],
            default=None,
        )
        
    else:
        # Use existing 12w and 4w logic
        # `power_thres` is optional for the presets and defaults to 15
        preset_power_thres = 15 if power_thres is None else power_thres
        data["target_metric_l12w"] = data.groupby("PersonId")["target_metric"].transform(
            lambda x: x.rolling(window=12, min_periods=1).mean()
        )
        data["target_metric_l4w"] = data.groupby("PersonId")["target_metric"].transform(
            lambda x: x.rolling(window=4, min_periods=1).mean()
        )

        # Identify habits
        habit_12w = identify_habit(data, metric="target_metric", threshold=1, width=9, max_window=12, return_type="data")
        habit_4w = identify_habit(data, metric="target_metric", threshold=1, width=4, max_window=4, return_type="data")

        habit_12w = habit_12w.rename(columns={"IsHabit": "IsHabit12w"})[["PersonId", "MetricDate", "IsHabit12w"]]
        habit_4w = habit_4w.rename(columns={"IsHabit": "IsHabit4w"})[["PersonId", "MetricDate", "IsHabit4w"]]

        # Merge habits back into the main dataset
        data = data.merge(habit_12w, on=["PersonId", "MetricDate"], how="left")
        data = data.merge(habit_4w, on=["PersonId", "MetricDate"], how="left")

        # Define usage segments
        data["UsageSegments_12w"] = np.select(
            [
                (data["IsHabit12w"] == True) & (data["target_metric_l12w"] >= preset_power_thres),
                (data["IsHabit12w"] == True),
                (data["target_metric_l12w"] >= 1),
                (data["target_metric_l12w"] > 0),
                (data["target_metric_l12w"] == 0),
            ],
            ["Power User", "Habitual User", "Novice User", "Low User", "Non-user"],
            default=None,
        )

        data["UsageSegments_4w"] = np.select(
            [
                (data["IsHabit4w"] == True) & (data["target_metric_l4w"] >= preset_power_thres),
                (data["IsHabit4w"] == True),
                (data["target_metric_l4w"] >= 1),
                (data["target_metric_l4w"] > 0),
                (data["target_metric_l4w"] == 0),
            ],
            ["Power User", "Habitual User", "Novice User", "Low User", "Non-user"],
            default=None,
        )

    if return_type == "data":
        return data
    elif return_type == "plot":
        if version == "12w":
            return plot_ts_us(data, cus="UsageSegments_12w", caption="Usage Segments - 12 weeks")
        elif version == "4w":
            return plot_ts_us(data, cus="UsageSegments_4w", caption="Usage Segments - 4 weeks")
        elif version is None:
            custom_caption = f"Usage Segments - Custom (threshold={threshold}, width={width}, max_window={max_window}w, power_thres={power_thres})"
            return plot_ts_us(data, cus="UsageSegments", caption=custom_caption)
        else:
            raise ValueError("Please provide either `12w`, `4w`, or None to `version`.")
    elif return_type == "table":
        # Create summary table with MetricDate as rows and segments as columns
        if version == "12w":
            segment_col = "UsageSegments_12w"
            print(f"Usage segments generated with 12-week parameters: threshold=1, width=9, max_window=12, power_thres={15 if power_thres is None else power_thres}")
        elif version == "4w":
            segment_col = "UsageSegments_4w"
            print(f"Usage segments generated with 4-week parameters: threshold=1, width=4, max_window=4, power_thres={15 if power_thres is None else power_thres}")
        elif version is None:
            segment_col = "UsageSegments"
            # Diagnostic message already printed above
        else:
            raise ValueError("Please provide either `12w`, `4w`, or None to `version`.")
            
        # Create pivot table
        summary_table = (
            data.groupby(["MetricDate", segment_col], as_index=False)
            .agg(count=("PersonId", "nunique"))
        )
        summary_table = summary_table.pivot(index="MetricDate", columns=segment_col, values="count").fillna(0)
        
        # Ensure all usage segment categories are present
        expected_segments = ["Non-user", "Low User", "Novice User", "Habitual User", "Power User"]
        for segment in expected_segments:
            if segment not in summary_table.columns:
                summary_table[segment] = 0
        
        # Reorder columns to match expected order
        summary_table = summary_table[expected_segments]
        
        return summary_table
    else:
        raise ValueError("Invalid return_type. Choose 'data', 'plot', or 'table'.")


def plot_ts_us(data, cus, caption,figsize=None):
    """Plot usage segments over time as a stacked bar chart.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataset with usage segments and a ``MetricDate`` column.
    cus : str
        Column name containing usage segment classifications.
    caption : str
        Caption text displayed below the chart.
    figsize : tuple or None, default None
        Figure size ``(width, height)`` in inches.  Defaults to ``(8, 6)``.

    Returns
    -------
    matplotlib.figure.Figure
        A stacked bar plot of usage segments over time.
    """
    # Group data and calculate proportions
    data = data.groupby(["MetricDate", cus]).size().reset_index(name="count")
    data["proportion"] = data.groupby("MetricDate")["count"].transform(lambda x: x / x.sum())

    # Pivot data for stacked bar plot
    pivot_data = data.pivot(index="MetricDate", columns=cus, values="proportion").fillna(0)

    # Define the order of categories and corresponding colors (reversed order for stacking)
    category_order = ["Non-user", "Low User", "Novice User", "Habitual User", "Power User"]
    colors = ["grey", "#808080", "#80baea", "#1c66b0", "#0c336e"]

    # Ensure all categories are present in the data
    for category in category_order:
        if category not in pivot_data.columns:
            pivot_data[category] = 0

    # Reorder columns to match the desired category order
    pivot_data = pivot_data[category_order]

    # Plot the stacked bar chart
    fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))
    plot_data = pivot_data.copy()
    plot_data.index = pivot_data.index.strftime("%Y-%m-%d")
    plot_data.plot(kind="bar", stacked=True, color=colors, ax=ax)

    # Customize the plot
    ax.set_title("Usage Segments", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Proportion of Users", fontsize=12)
    ax.legend(title="Usage Segment", fontsize=10)
    ax.set_xticks(range(len(pivot_data.index)))
    ax.set_xticklabels(plot_data.index, rotation=45, ha="right")
    ax.text(
        0, -0.15, caption, transform=ax.transAxes, fontsize=10, alpha=0.7, ha="left"
    )
    plt.tight_layout()
    return fig
