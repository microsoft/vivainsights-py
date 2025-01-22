# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
This script generate a summary of key metrics with options to return a heatmap or a summary table.
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def keymetrics_scan(data,
                    hrvar="Organization",
                    mingroup=5,
                    metrics=[
                        "Workweek_span", "Collaboration_hours", "After_hours_collaboration_hours", "Meetings",
                        "Meeting_hours", "After_hours_meeting_hours", "Low_quality_meeting_hours",
                        "Meeting_hours_with_manager_1_on_1", "Meeting_hours_with_manager", "Emails_sent",
                        "Email_hours", "After_hours_email_hours", "Generated_workload_email_hours",
                        "Total_focus_hours", "Internal_network_size", "Networking_outside_organization",
                        "External_network_size", "Networking_outside_company"
                    ],
                    return_type="plot",
                    low_color="#4169E1",
                    mid_color="#F1CC9E",
                    high_color="#D8182A",
                    textsize=10):    
    
    """
    Generate a summary of key metrics with options to return a heatmap or a summary table.

    Parameters:
    - data: pandas DataFrame containing the input data.
    - hrvar: Column name to group by, defaults to "Organization".
    - mingroup: Minimum number of employees required to include a group.
    - metrics: List of metric column names to calculate averages for.
    - return_type: "plot" for heatmap or "table" for summary table.
    - low, mid, high: Color codes for low, mid, and high values in the heatmap.
    - textsize: Font size for the text in the plot.

    Returns:
    - A seaborn heatmap (plot) or a summary table (DataFrame).
    """
    """
    Name
    ----
    keymetrics_scan

    Description
    ------------
    This function generates a summary of key metrics from a given dataset with options to return a heatmap visualization or a summary table.

    Parameters
    ----------
    data : pandas.DataFrame
        The input data containing the metrics to analyze.
    hrvar : str, optional
        The column name to group the data by. Defaults to `"Organization"`.
    mingroup : int, optional
        The minimum number of employees required to include a group in the analysis. Defaults to `5`.
    metrics : list of str, optional
        A list of metric column names to calculate averages for. Defaults to:
        - `"Workweek_span"`
        - `"Collaboration_hours"`
        - `"After_hours_collaboration_hours"`
        - `"Meetings"`
        - `"Meeting_hours"`
        - `"After_hours_meeting_hours"`
        - `"Low_quality_meeting_hours"`
        - `"Meeting_hours_with_manager_1_on_1"`
        - `"Meeting_hours_with_manager"`
        - `"Emails_sent"`
        - `"Email_hours"`
        - `"After_hours_email_hours"`
        - `"Generated_workload_email_hours"`
        - `"Total_focus_hours"`
        - `"Internal_network_size"`
        - `"Networking_outside_organization"`
        - `"External_network_size"`
        - `"Networking_outside_company"`
    return_type : str, optional
        Specifies the type of output to return. Valid values are:
        - `"plot"` (default): Generate a heatmap visualization.
        - `"table"`: Return a summary table as a pandas DataFrame.
    mid_color : str, optional
    high_color: str, optional
    low_color : str, optional
        Color codes for low, mid, and high values in the heatmap. Defaults to:
        - `low_color="#4169E1"` (blue)
        - `mid_color="#F1CC9E"` (beige)
        - `high_color="#D8182A"` (red)
        Color codes for low, mid, and high values in the heatmap. Can be set to:
        - `Black: "#000000"`
        - `White: "#FFFFFF"`
        - `Red: "#FF0000"`
        - `Lime: "#00FF00"`
        - `Blue: "#0000FF"`
        - `Yellow: "#FFFF00"`
        - `Cyan/Aqua: "#00FFFF"`
        - `Magenta/Fuchsia: "#FF00FF"`
        - `Silver: "#C0C0C0"`
        - `Gray: "#808080"`
        - `Maroon: "#800000"`
        - `Olive: "#808000"`
        - `Green: "#008000"`
        - `Purple: "#800080"`
        - `Teal: "#008080"`
        - `Navy: "#000080"`
        - `Light Gray: "#D3D3D3"`
        - `Dark Gray: "#A9A9A9"`
        - `Dim Gray: "#696969"`
        - `Slate Gray: "#708090"`
        - `Light Slate Gray: "#778899"`
        - `Crimson: "#DC143C"`
        - `Coral: "#FF7F50"`
        - `Tomato: "#FF6347"`
        - `Orange: "#FFA500"`
        - `Gold: "#FFD700"`
        - `Dark Orange: "#FF8C00"`
        - `Light Salmon: "#FFA07A"`
        - `Dodger Blue: "#1E90FF"`
        - `Sky Blue: "#87CEEB"`
        - `Steel Blue: "#4682B4"`
        - `Light Blue: "#ADD8E6"`
        - `Dark Blue: "#00008B"`
        - `Medium Blue: "#0000CD"`
        - `Royal Blue: "#4169E1"`
        - `Sienna: "#A0522D"`
        - `Saddle Brown: "#8B4513"`
        - `Chocolate: "#D2691E"`
        - `Peru: "#CD853F"`
        - `Sandy Brown: "#F4A460"`
        - `Tan: "#D2B48C"`
        - `Lavender: "#E6E6FA"`
        - `Thistle: "#D8BFD8"`
        - `Plum: "#DDA0DD"`
        - `Orchid: "#DA70D6"`
        - `Peach Puff: "#FFDAB9"`
        - `Mint Cream: "#F5FFFA"`
        - `Forest Green: "#228B22"`
        - `Sea Green: "#2E8B57"`
        - `Medium Sea Green: "#3CB371"`
        - `Spring Green: "#00FF7F"`
        - `Pale Green: "#98FB98"`
        - `Indian Red: "#CD5C5C"`
        - `Rosy Brown: "#BC8F8F"`
        - `Hot Pink: "#FF69B4"`
        - `Deep Pink: "#FF1493"`
        - `Light Pink: "#FFB6C1"`
        - `Midnight Blue: "#191970"`
        - `Cornflower Blue: "#6495ED"`
        - `Powder Blue: "#B0E0E6"`
        - `Light Sky Blue: "#87CEFA"`
    textsize : int, optional
        Font size for text elements in the heatmap. Defaults to `10`.

    Returns
    -------
    - If `return_type="plot"`: Displays a heatmap visualization of the rescaled key metrics grouped by the specified HR attribute.
    - If `return_type="table"`: Returns a pandas DataFrame containing a summary table of average metric values grouped by the specified HR attribute.

    Raises
    ------
    ValueError
        - If none of the specified metrics are present in the dataset.
        - If no data is available after applying the `mingroup` filter.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.keymetrics_scan(data=pq_data, hrvar="Organization", mingroup=10, return_type="table")
    # Returns a summary table grouped by "Team" with a minimum group size of 10.

    >>> vi.keymetrics_scan(data=pq_data, hrvar="Organization", metrics=["Workweek_span", "Meeting_hours"], return_type="plot")
    # Displays a heatmap of the rescaled "Workweek_span" and "Meeting_hours" metrics grouped by "Department".

    >>> vi.keymetrics_scan(data=pq_data, low_color="#4169E1", mid_color="#F1CC9E", high_color="#D8182A", textsize=12)
    # Generates a heatmap using the low mid and high color palette with font size 12.

    """    
    # Default group handling
    if hrvar is None:
        data['Total'] = "Total"
        hrvar = "Total"

    # Filter metrics available in the data
    metrics = [metric for metric in metrics if metric in data.columns]
    if not metrics:
        raise ValueError("None of the specified metrics are available in the data.")

    # Group and summarize the data
    grouped = (data.groupby([hrvar, "PersonId"])[metrics]
               .mean()
               .groupby(hrvar)
               .mean()
               .reset_index())

    employee_count = data.groupby(hrvar)['PersonId'].count().reset_index(name="Employee_Count")
    summary_table = pd.merge(grouped, employee_count, on=hrvar)
    summary_table = summary_table[summary_table["Employee_Count"] >= mingroup]

    if summary_table.empty:
        raise ValueError(f"No data available after applying `mingroup` filter of {mingroup}.")

    # Rescale values for visualization
    summary_long = summary_table.melt(id_vars=[hrvar], var_name="Metric", value_name="Value")
    summary_long["Value_Rescaled"] = (
        summary_long.groupby("Metric")["Value"]
        .transform(lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else 0))

    if return_type == "table":
        return summary_table

    elif return_type == "plot":
        plt.figure(figsize=(12, 8))

        # Custom colormap
        custom_cmap = LinearSegmentedColormap.from_list(
            "custom_cmap", [low_color, mid_color, high_color]
        )

        heatmap_data = summary_long[summary_long["Metric"] != "Employee_Count"]
        heatmap_pivot = heatmap_data.pivot(index="Metric", columns=hrvar, values="Value_Rescaled")

        sns.heatmap(
            heatmap_pivot,
            cmap=custom_cmap,
            annot=True,
            cbar=True,
            cbar_kws={"label": "Rescaled Value"},
            fmt=".1f"
        )

        plt.title(f"Key Metrics\nWeekly average by {hrvar}", fontsize=16)
        plt.ylabel("")
        plt.xlabel("")
        plt.xticks(rotation=90, fontsize=textsize)
        plt.yticks(fontsize=textsize)
        plt.show()

    else:
        raise ValueError("Invalid value for `return_type`. Choose 'plot' or 'table'.")