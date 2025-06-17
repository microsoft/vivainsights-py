# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
The function `create_bubble` creates a bubble visualization and summary table for a given metric
and grouping variable in a dataset.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import to_hex
from adjustText import adjust_text
from vivainsights.totals_col import totals_col
from matplotlib.lines import Line2D

def create_bubble(data, metric_x, metric_y, hrvar="Organization", mingroup=5, return_type="plot", bubble_size=(1, 100)):
    """
    Generates a bubble plot or a summary table based on two selected metrics.

    Parameters
    ----------
    - data (pd.DataFrame): The dataset containing the metrics and employee details.
    - metric_x (str): Column name representing the x-axis metric.
    - metric_y (str): Column name representing the y-axis metric.
    - hrvar (str): HR variable to group by. Defaults to "Organization".
    - mingroup (int): Minimum group size threshold. Defaults to 5.
    - return_type (str): "plot" to return a bubble plot, "table" to return a summary table.
    - bubble_size (tuple): Size range for the bubbles in the plot.

    Returns
    -------
    - If return_type == "plot", returns a seaborn scatter plot with bubble sizes.
    - If return_type == "table", returns a pandas DataFrame with the summarized metrics.

    Example
    -------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.create_bubble(data=pq_data, metric_x="Collaboration_hours", metric_y="Multitasking_hours", hrvar="Organization")
    """
    # Handling NULL values passed to hrvar
    if(hrvar is None):
        data = totals_col(data)
        hrvar = "Total"
            
    col_highlight = "#fe7f4f"
    # Input checks
    required_variables = [hrvar, metric_x, metric_y, "PersonId"]
    for var in required_variables:
        if var not in data.columns:
            raise ValueError(f"Missing required variable: {var}")

    # Clean metric names
    clean_x = metric_x.replace('_', ' ')
    clean_y = metric_y.replace('_', ' ')

    # Group and summarize data
    myTable = data.groupby(['PersonId', hrvar]).agg({metric_x: 'mean', metric_y: 'mean'}).reset_index()
    myTable = myTable.groupby(hrvar).agg({metric_x: 'mean', metric_y: 'mean', 'PersonId': 'count'}).reset_index()
    myTable = myTable.rename(columns={'PersonId': 'n'})
    myTable = myTable[myTable['n'] >= mingroup]

    # Plotting
    if return_type == "plot":
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Reserve more space for title/subtitle/orange line
        plt.subplots_adjust(top=0.82)
        
        # Scatterplot
        sns.scatterplot(data=myTable, x=metric_x, y=metric_y, size='n', sizes=bubble_size,
                        alpha=0.5, color=to_hex((0, 120/255, 212/255)), ax=ax)
        
        # Bubble labels
        texts = [ax.text(row[metric_x], row[metric_y], row[hrvar], size=8) for _, row in myTable.iterrows()]
        adjust_text(texts, ax=ax)
        
        # Title and subtitle using fig.text (not ax.text) for exact positioning
        fig.text(0.1, 0.95, f"{clean_x} and {clean_y}", ha='left', fontsize=14, weight='bold', alpha=0.9)
        fig.text(0.1, 0.91, f"By {hrvar.replace('_', ' ')}", ha='left', fontsize=12, alpha=0.85)
        
        # Orange decorative line (below subtitle)
        fig.lines.append(
            Line2D(
                [0.1, 0.9], [0.89, 0.89],  # y = just below subtitle
                transform=fig.transFigure,
                color=col_highlight,
                linewidth=0.6,
                clip_on=False
            )
        )
        
        # Orange rectangle block
        fig.patches.extend([
            plt.Rectangle(
                (0.1, 0.89), 0.05, -0.015,
                facecolor=col_highlight,
                transform=fig.transFigure,
                clip_on=False,
                linewidth=0
            )
        ])
        
        # Axes labels
        ax.set_xlabel(clean_x)
        ax.set_ylabel(clean_y)
        
        # Caption
        fig.text(0.1, 0.02, f"Total employees = {myTable['n'].sum()} | {pd.to_datetime(data['MetricDate']).min().strftime('%Y-%m-%d')} to {pd.to_datetime(data['MetricDate']).max().strftime('%Y-%m-%d')}", fontsize=8)

        return fig

    elif return_type == "table":
        return myTable
    else:
        raise ValueError("Please enter a valid input for `return_type`.")