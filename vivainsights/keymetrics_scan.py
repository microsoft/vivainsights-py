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
                    color_palette="Spectral",
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
    color_palette : str, optional
        - `"coolwarm"`
        - `"RdBu"`
        - `"Spectral"`
        - `"PiYG"`
        - `"PRGn"`
        - `"BrBG"`
        - `"RdYlBu"`
        - `"RdYlGn"`
        - `"Blues"`
        - `"Reds"`
        - `"Greens"`
        - `"Oranges"`
        - `"Purples"`
        - `"Greys"`
        - `"YlGn"`
        - `"YlGnBu"`
        - `"PuBu"`
        - `"BuPu"`
        - `"PuRd"`
        - `"RdPu"`
        - `"viridis"`
        - `"plasma"`
        - `"cividis"`
        - `"magma"`
        - `"inferno"`
        - `"tab10"`
        - `"tab20"`
        - `"Set1"`
        - `"Set2"`
        - `"Set3"`
        - `"Pastel1"`
        - `"Pastel2"`
        - `"Accent"`
        - `"Dark2"`
        - `"twilight"`
        - `"twilight_shifted"`
        - `"hsv"`
        Specifies the color palette for the heatmap. Defaults to `"Spectral"`.
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
    >>> keymetrics_scan(data=my_data, hrvar="Team", mingroup=10, return_type="table")
    # Returns a summary table grouped by "Team" with a minimum group size of 10.

    >>> keymetrics_scan(data=my_data, hrvar="Department", metrics=["Workweek_span", "Meeting_hours"], return_type="plot")
    # Displays a heatmap of the rescaled "Workweek_span" and "Meeting_hours" metrics grouped by "Department".

    >>> keymetrics_scan(data=my_data, color_palette="coolwarm", textsize=12)
    # Generates a heatmap using the "coolwarm" color palette with font size 12.

    """    
    # Check if hrvar is available in the data
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
    # Reshape for heatmap
    if summary_table.empty:
        raise ValueError(f"No data available after applying `mingroup` filter of {mingroup}.")
    
    summary_long = summary_table.melt(id_vars=[hrvar], var_name="Metric", value_name="Value")
    summary_wide = summary_long.pivot(index="Metric", columns=hrvar, values="Value")
    summary_long["Value_Rescaled"] = (
    summary_long.groupby("Metric")["Value"]
    .transform(lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else 0))

    if return_type == "table":
        return summary_wide

    elif return_type == "plot":
        plt.figure(figsize=(12, 8))
        heatmap_data = summary_long[summary_long["Metric"] != "Employee_Count"]
        heatmap_pivot = heatmap_data.pivot(index="Metric", columns=hrvar, values="Value_Rescaled")
        cmap = sns.color_palette(color_palette, as_cmap=True)
        sns.heatmap(heatmap_pivot, fmt=".1f", cmap=cmap,annot=True, cbar=True,cbar_kws={"label": "Rescaled Value"})
        plt.title("Key Metrics\nWeekly average by " + hrvar, fontsize=16)
        plt.ylabel("")
        plt.xlabel("")
        plt.xticks(rotation=90)
        plt.show()

    else:
        raise ValueError("Please enter a valid input for `return_type`.")