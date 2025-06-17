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
from vivainsights.extract_date_range import extract_date_range
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D

def keymetrics_scan(data,
                    hrvar="Organization",
                    mingroup=5,
                    metrics=["Workweek_span",
                             "Collaboration_hours",
                             "After_hours_collaboration_hours",
                             "Meetings",
                             "Meeting_hours",
                             "After_hours_meeting_hours",
                             "Low_quality_meeting_hours",
                             "Meeting_hours_with_manager_1_on_1",
                             "Meeting_hours_with_manager",
                             "Emails_sent",
                             "Email_hours",
                             "After_hours_email_hours",
                             "Generated_workload_email_hours",
                             "Total_focus_hours",
                             "Internal_network_size",
                             "Networking_outside_organization",
                             "External_network_size",
                             "Networking_outside_company"],
                    return_type="plot",
                    low_color="#4169E1",
                    mid_color="#F1CC9E",
                    high_color="#D8182A",
                    textsize=10,
                    plot_row_scaling_factor=0.8):    
    """
    Name
    ----
    keymetrics_scan

    Description
    ------------
    Generate a summary of key metrics with options to return a heatmap or a summary table.

    Parameters
    ----------
    data : pandas.DataFrame
        A Person Query dataset in the form of a pandas dataframe.
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
        data['Total'] = 'Total'
        hrvar = 'Total'

    # Filter metrics present in the data
    metrics = [metric for metric in metrics if metric in data.columns]

    # Compute summary table
    summary_table = (
        data.groupby([hrvar, 'PersonId'])[metrics]
        .mean()
        .groupby(hrvar)
        .mean()
        .reset_index()
    )

    # Add employee count
    employee_count = (
        data.groupby(hrvar)['PersonId']
        .nunique()
        .reset_index()
        .rename(columns={"PersonId": "Employee_Count"})
    )

    summary_table = summary_table.merge(employee_count, on=hrvar)
    summary_table = summary_table[summary_table['Employee_Count'] >= mingroup]

    # Melt the summary table for visualization
    summary_long = (
        summary_table.melt(id_vars=[hrvar], var_name="variable", value_name="value")
    )

    # Prepare the heatmap with row-wise normalization
    if return_type == "plot":
        variables = summary_long['variable'].unique()
        num_vars = len(variables)
        hrvar_categories = summary_long[hrvar].unique()
        cap_str = extract_date_range(data, return_type='text')

        title_text = "Key Metrics - Weekly Average"
        subtitle_text = f"By {hrvar.replace('_', ' ')}"

        fig, axes = plt.subplots(num_vars, 1, figsize=(10, plot_row_scaling_factor * num_vars), sharex=True)

        for i, variable in enumerate(variables):
            custom_cmap = LinearSegmentedColormap.from_list("custom_cmap", [low_color, mid_color, high_color])
            ax = axes[i] if num_vars > 1 else axes
            subset = summary_long[summary_long['variable'] == variable]
            row_min = subset['value'].min()
            row_max = subset['value'].max()

            normalized_values = (subset['value'] - row_min) / (row_max - row_min)
            heatmap_data = pd.DataFrame([normalized_values.values], columns=hrvar_categories)

            sns.heatmap(heatmap_data,
                        annot=subset['value'].values.reshape(1, -1),
                        fmt=".1f",
                        cmap=custom_cmap,
                        cbar=False,
                        linewidths=0.5,
                        vmin=0,
                        vmax=1,
                        yticklabels=False,
                        ax=ax)

            if i == 0:
                ax.xaxis.tick_top()
                ax.tick_params(axis='x', labeltop=True, labelbottom=False, labelrotation=45, pad=10)
            else:
                ax.tick_params(axis='x', bottom=False, labelbottom=False)

            ax.set_ylabel(variable, fontsize=textsize, rotation=0, labelpad=5, ha="right")
            ax.tick_params(left=False)

        fig.text(0.01, 0.995, title_text, fontsize=16, weight='bold', ha='left', va='top')
        fig.text(0.01, 0.965, subtitle_text, fontsize=12, ha='left', va='top', alpha=0.85)

        line = Line2D([0.01, 1.0], [0.910, 0.910], transform=fig.transFigure,
              color='#fe7f4f', linewidth=1.2, clip_on=False)
        fig.add_artist(line)


        rect = plt.Rectangle((0.01, 0.910), 0.03, -0.015,
                             transform=fig.transFigure,
                             facecolor='#fe7f4f',
                             clip_on=False,
                             linewidth=0)
        fig.add_artist(rect)

        fig.text(0.01, 0.01, cap_str, ha='left', fontsize=9, alpha=0.7)

        plt.tight_layout(rect=[0, 0.03, 1, 0.93])
        return fig

    elif return_type == "table":
        return summary_table

    else:
        raise ValueError("Invalid value for `return_type`. Choose either 'plot' or 'table'.")
