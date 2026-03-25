# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Generate a heatmap or summary table scanning key Viva Insights metrics.
"""

__all__ = ['keymetrics_scan']

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from vivainsights.extract_date_range import extract_date_range
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from vivainsights.us_to_space import us_to_space

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
    Generate a summary heatmap or table scanning key Viva Insights metrics.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.
    hrvar : str, optional
        Column name to group by. Defaults to ``"Organization"``.
    mingroup : int, optional
        Minimum group size to include. Defaults to 5.
    metrics : list of str, optional
        Metric column names to calculate averages for. Defaults to a
        standard set of Viva Insights metrics (see source).
    return_type : str, optional
        ``"plot"`` (default) returns a heatmap; ``"table"`` returns a
        summary DataFrame.
    low_color : str, optional
        Hex colour for low heatmap values. Defaults to ``"#4169E1"``.
    mid_color : str, optional
        Hex colour for mid heatmap values. Defaults to ``"#F1CC9E"``.
    high_color : str, optional
        Hex colour for high heatmap values. Defaults to ``"#D8182A"``.
    textsize : int, optional
        Font size for heatmap annotations. Defaults to 10.
    plot_row_scaling_factor : float, optional
        Scaling factor for plot row height. Defaults to 0.8.

    Returns
    -------
    matplotlib.figure.Figure or pandas.DataFrame
        Heatmap figure or summary table depending on ``return_type``.

    Raises
    ------
    ValueError
        If no specified metrics exist in the data or if no groups remain
        after applying ``mingroup``.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.keymetrics_scan(data=pq_data, hrvar="Organization", mingroup=10, return_type="table")
    >>>
    >>> vi.keymetrics_scan(data=pq_data, metrics=["Workweek_span", "Meeting_hours"], return_type="plot")
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
    # Add Employee_Count to metrics used in plotting
    summary_table_columns = [col for col in summary_table.columns if col != hrvar]
    summary_long = summary_table.melt(id_vars=[hrvar], var_name="variable", value_name="value")


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
            ax = axes[i] if num_vars > 1 else axes
            subset = summary_long[summary_long['variable'] == variable]
            values = subset['value'].values
            row_data = pd.DataFrame([values], columns=hrvar_categories)

            if variable == "Employee_Count":
                light_gray_cmap = LinearSegmentedColormap.from_list("gray_cmap", ["#FFFFFF", "#FFFFFF"])
                sns.heatmap(row_data,
                            annot=values.reshape(1, -1),
                            fmt=".0f",
                            cmap=light_gray_cmap,
                            cbar=False,
                            linewidths=0.5,
                            vmin=0,
                            vmax=1,
                            yticklabels=False,
                            ax=ax)
            else:
                row_min = subset['value'].min()
                row_max = subset['value'].max()
                normalized_values = (values - row_min) / (row_max - row_min)
                norm_data = pd.DataFrame([normalized_values], columns=hrvar_categories)

                custom_cmap = LinearSegmentedColormap.from_list("custom_cmap", [low_color, mid_color, high_color])
                sns.heatmap(norm_data,
                            annot=values.reshape(1, -1),
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

            ax.set_ylabel(us_to_space(variable), fontsize=textsize, rotation=0, labelpad=5, ha="right")
            ax.tick_params(left=False)

        fig.text(0.01, 0.995, title_text, fontsize=16, weight='bold', ha='left', va='top')
        fig.text(0.01, 0.905, subtitle_text, fontsize=12, ha='left', va='top', alpha=0.85)

        line = Line2D([0.01, 1.0], [0.85, 0.85], transform=fig.transFigure,
              color='#fe7f4f', linewidth=1.2, clip_on=False)
        fig.add_artist(line)

        rect = plt.Rectangle((0.01, 0.85), 0.03, -0.015,
                             transform=fig.transFigure,
                             facecolor='#fe7f4f',
                             clip_on=False,
                             linewidth=0)
        fig.add_artist(rect)

        fig.text(0.01, 0.01, cap_str, ha='left', fontsize=9, alpha=0.7)

        plt.tight_layout(rect=[0, 0.03, 1, 0.85])
        return fig

    elif return_type == "table":
        return summary_table

    else:
        raise ValueError("Invalid value for `return_type`. Choose either 'plot' or 'table'.")
