# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from vivainsights.identify_habit import identify_habit


def identify_usage_segments(data, metric=None, metric_str=None, version="12w", return_type="data", 
                          threshold=None, width=None, max_window=None, power_thres=None):
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
        Version of classification: "12w" (12-week rolling average), "4w" (4-week rolling average), or None for custom parameters. Default is "12w".
    figsize : tuple, optional
        The `figsize` parameter is an optional tuple that specifies the size of the figure for the boxplot visualization. It should be in the format `(width, height)`, where `width` and `height` are in inches. If not provided, a default size of (8, 6) will be used.        
    return_type : str, optional
        What to return: "data" (default), "plot", or "table".
    threshold : int, optional
        Threshold for habit identification. Required when version=None.
    width : int, optional
        Width parameter for habit identification. Required when version=None.
    max_window : int, optional
        Maximum window for habit identification. Required when version=None.
    power_thres : float, optional
        Power user threshold for usage segment classification. Required when version=None.

    Returns
    -------
    pandas.DataFrame or matplotlib.figure.Figure
        Depending on `return_type`, returns a DataFrame with usage segments, a plot visualizing the segments over time, or a summary table.

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
    
    # Example usage with custom parameters
    >>> result = vi.identify_usage_segments(
    >>>     data=pq_data,
    >>>     metric="Emails_sent",
    >>>     version=None,
    >>>     threshold=2,
    >>>     width=5,
    >>>     max_window=8,
    >>>     power_thres=20,
    >>>     return_type="table"
    >>> )
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
        elif version is None:
            custom_caption = f"Usage Segments - Custom (threshold={threshold}, width={width}, max_window={max_window}w, power_thres={power_thres})"
            return plot_ts_us(data, cus="UsageSegments", caption=custom_caption)
        else:
            raise ValueError("Please provide either `12w`, `4w`, or None to `version`.")
    elif return_type == "table":
        # Create summary table with MetricDate as rows and segments as columns
        if version == "12w":
            segment_col = "UsageSegments_12w"
            print("Usage segments generated with 12-week parameters: threshold=1, width=9, max_window=12, power_thres=15")
        elif version == "4w":
            segment_col = "UsageSegments_4w"
            print("Usage segments generated with 4-week parameters: threshold=1, width=4, max_window=4, power_thres=15")
        elif version is None:
            segment_col = "UsageSegments"
            # Diagnostic message already printed above
        else:
            raise ValueError("Please provide either `12w`, `4w`, or None to `version`.")
            
        # Create pivot table
        summary_table = (
            data.groupby(["MetricDate", segment_col])
            .size()
            .reset_index(name="count")
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
    fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))
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
