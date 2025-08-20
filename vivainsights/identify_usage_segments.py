# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from vivainsights.identify_habit import identify_habit


def identify_usage_segments(data, metric=None, metric_str=None, version="12w", return_type="data"):
    """
    Identify usage segments based on a metric.

    Parameters
    ----------
    data : pandas.DataFrame
        A dataset containing the metric to be classified. Must include 'PersonId' and 'MetricDate' columns.
    metric : str, optional
        Name of the metric column to classify.
    metric_str : list of str, optional
        List of metric columns to aggregate for classification.
    version : str, optional
        Version of classification: "12w" (12-week rolling average) or "4w" (4-week rolling average). Default is "12w".
    return_type : str, optional
        What to return: "data" (default) or "plot".

    Returns
    -------
    pandas.DataFrame or matplotlib.figure.Figure
        Depending on `return_type`, returns a DataFrame with usage segments or a plot visualizing the segments over time.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()

    # Example usage with a single metric column
    >>> vi.identify_usage_segments(data=pq_data, metric="Emails_sent", version="12w", return_type="data")

    # Example usage with multiple metric columns
    >>> result = vi.identify_usage_segments(
    >>>     data=pq_data,
    >>>     metric_str=[
    >>>         "Copilot_actions_taken_in_Teams",
    >>>         "Copilot_actions_taken_in_Outlook",
    >>>         "Copilot_actions_taken_in_Excel",
    >>>         "Copilot_actions_taken_in_Word",
    >>>         "Copilot_actions_taken_in_Powerpoint"
    >>>     ],
    >>>     version="4w",
    >>>     return_type="plot"
    >>> )
    >>> result.show()
    """
    if metric is None and metric_str is None:
        raise ValueError("Please provide either a metric or a metric_str.")
    if metric is not None and metric_str is not None:
        raise ValueError("Please provide either a metric or a metric_str, not both.")

    # Prepare the target metric
    if metric is not None:
        data["target_metric"] = data[metric]
    else:
        data["target_metric"] = data[metric_str].sum(axis=1, skipna=True)

    # Create rolling averages
    data = data.sort_values(by=["PersonId", "MetricDate"])
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
            (data["IsHabit12w"] == True) & (data["target_metric_l12w"] >= 15),
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
            (data["IsHabit4w"] == True) & (data["target_metric_l4w"] >= 15),
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
        else:
            raise ValueError("Please provide either `12w` or `4w` to `version`.")
    else:
        raise ValueError("Invalid return_type. Choose 'data' or 'plot'.")


def plot_ts_us(data, cus, caption):
    """
    Plot usage segments over time.

    Parameters
    ----------
    data : pandas.DataFrame
        A dataset containing the usage segments and 'MetricDate' column.
    cus : str
        Column name containing the usage segment classifications.
    caption : str
        Caption for the plot.

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
    fig, ax = plt.subplots(figsize=(8, 6))
    pivot_data.plot(kind="bar", stacked=True, color=colors, ax=ax)

    # Customize the plot
    ax.set_title("Usage Segments", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Proportion of Users", fontsize=12)
    ax.legend(title="Usage Segment", fontsize=10)
    ax.set_xticks(range(len(pivot_data.index)))
    ax.set_xticklabels(pivot_data.index.strftime("%Y-%m-%d"), rotation=45, ha="right")
    ax.text(
        0, -0.15, caption, transform=ax.transAxes, fontsize=10, alpha=0.7, ha="left"
    )
    plt.tight_layout()
    return fig
