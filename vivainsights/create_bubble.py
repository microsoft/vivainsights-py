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
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=myTable, x=metric_x, y=metric_y, size='n', sizes=bubble_size, alpha=0.5, 
                        color=to_hex((0, 120/255, 212/255)), ax=ax)
        texts = [ax.text(row[metric_x], row[metric_y], row[hrvar], size=8) for _, row in myTable.iterrows()]
        adjust_text(texts, ax=ax)
        # --- Title/subtitle split ---
        ax.set_title(f"{clean_x} and {clean_y}", fontsize=14, weight='bold', alpha=0.85, loc='left', pad=18)
        ax.text(0, 1.02, f"By {hrvar.replace('_', ' ')}", transform=ax.transAxes, fontsize=12, alpha=0.85, ha='left')
        ax.set_xlabel(clean_x)
        ax.set_ylabel(clean_y)
        fig.text(0.1, -0.1, f"Total employees = {myTable['n'].sum()} | {pd.to_datetime(data['MetricDate']).min().strftime('%Y-%m-%d')} to {pd.to_datetime(data['MetricDate']).max().strftime('%Y-%m-%d')}", fontsize=8)

        # --- Add orange line and rectangle at the top ---
        # Orange color: #fe7f4f
        ax.plot(
            [0, .9],  # width of line
            [1.00, 1.00],  # height of line (above title/subtitle)
            transform=fig.transFigure,
            clip_on=False,
            color='#fe7f4f',
            linewidth=.6
        )
        ax.add_patch(
            plt.Rectangle(
                (0, 1.00),  # left, bottom
                0.05,       # width
                -0.025,     # height (negative to go up)
                facecolor='#fe7f4f',
                transform=fig.transFigure,
                clip_on=False,
                linewidth=0
            )
        )

        return fig

    elif return_type == "table":
        return myTable
    else:
        raise ValueError("Please enter a valid input for `return_type`.")