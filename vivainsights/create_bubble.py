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
    >>> vi.create_bubble(pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation")
    """

    # Input checks
    required_variables = [hrvar, metric_x, metric_y, "PersonId"]
    for var in required_variables:
        if var not in data.columns:
            raise ValueError(f"Missing required variable: {var}")

    # Handling NULL values passed to hrvar
    if hrvar is None:
        data['Total'] = 'Total'
        hrvar = 'Total'

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
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=myTable, x=metric_x, y=metric_y, size='n', sizes=bubble_size, alpha=0.5, color=to_hex((0, 120/255, 212/255)))
        texts = [plt.text(row[metric_x], row[metric_y], row[hrvar], size=8) for idx, row in myTable.iterrows()]
        adjust_text(texts)
        plt.title(f"{clean_x} and {clean_y} By {hrvar.replace('_', ' ')}")
        plt.xlabel(clean_x)
        plt.ylabel(clean_y)
        # plt.suptitle(f"By {hrvar.replace('_', ' ')}", y=0.95, fontsize=10)
        plt.figtext(0.1, -0.1, f"Total employees = {myTable['n'].sum()} | {pd.to_datetime(data['Date']).min().strftime('%Y-%m-%d')} to {pd.to_datetime(data['Date']).max().strftime('%Y-%m-%d')}", fontsize=8)
        plt.show()
    elif return_type == "table":
        return myTable
    else:
        raise ValueError("Please enter a valid input for `return_type`.")