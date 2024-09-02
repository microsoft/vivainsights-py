# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module generates Gini coefficient calculation, Lorenz curve generation, and plotting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_value_proportion(df, population_share):
    """
    Calculate the proportion of total values (e.g., income, email sent) 
    that corresponds to a given cumulative share of the population.

    Parameters:
    df (pd.DataFrame): DataFrame containing cumulative population and value proportions.
    population_share (float): The cumulative share of the population (between 0 and 1).

    Returns:
    float: The proportion of total values corresponding to the given population share.

    Raises:
    ValueError: If population_share is not between 0 and 1.
    """
    if population_share < 0 or population_share > 1:
        raise ValueError("Population share must be between 0 and 1")

    # Find the row in the DataFrame where the cumulative population meets or exceeds the input share
    closest_row = df[df['cum_population'] >= population_share].iloc[0]
    return closest_row['cum_values_prop']

def compute_gini(x):
    """
    Compute the Gini coefficient, a measure of statistical dispersion 
    representing income or wealth inequality.

    Parameters:
    x (list, np.ndarray, pd.Series): A numeric vector representing values (e.g., income, emails sent).

    Returns:
    float: The Gini coefficient for the given vector of values.

    Raises:
    ValueError: If input is not a numeric vector.
    """
    if not isinstance(x, (list, np.ndarray, pd.Series)):
        raise ValueError("Input must be a numeric vector")

    # Sort the values in ascending order
    x = np.sort(x)
    n = len(x)

    # Calculate the Gini coefficient using the formula
    gini = (2 * np.sum((np.arange(1, n + 1)) * x) - (n + 1) * np.sum(x)) / (n * np.sum(x))
    return gini

def create_lorenz(data, metric, return_type="gini"):
    """
    Calculate and return the Lorenz curve and Gini coefficient for a given metric.

    Parameters:
    data (pd.DataFrame): DataFrame containing the data to analyze.
    metric (str): The column name in the DataFrame representing the values to analyze.
    return_type (str): The type of output to return: 
                       - "gini" (default): returns the Gini coefficient.
                       - "table": returns a DataFrame of cumulative population and value shares.
                       - "plot": displays a Lorenz curve plot with the Gini coefficient.

    Returns:
    float/pd.DataFrame/None: Depending on return_type:
                             - "gini": returns the Gini coefficient.
                             - "table": returns a DataFrame of population and value shares.
                             - "plot": displays the Lorenz curve plot.

    Raises:
    ValueError: If the metric is not found in the DataFrame, or if an invalid return_type is specified.
    
    
    Example
    --------
    Assuming `pq_data` is a DataFrame with an "Emails_sent" column.
    >>> gini = create_lorenz(data=pq_data, metric="Emails_sent", return_type="gini")
    
    >>> lorenz_table = create_lorenz(data=pq_data, metric="Emails_sent", return_type="table")
    
    >>> create_lorenz(data=pq_data, metric="Emails_sent", return_type="plot")
    
    """
    if metric not in data.columns:
        raise ValueError(f"Metric '{metric}' not found in data.")

    n = data[metric]

    # Create a DataFrame sorted by the metric to analyze
    lorenz_df = pd.DataFrame({
        'n': n
    }).sort_values(by='n')

    # Calculate cumulative sums for values and population
    lorenz_df['cum_values'] = lorenz_df['n'].cumsum()
    lorenz_df['cum_population'] = np.cumsum(np.ones(len(lorenz_df))) / len(lorenz_df)
    lorenz_df['cum_values_prop'] = lorenz_df['cum_values'] / lorenz_df['n'].sum()

    if return_type == "gini":
        # Return the Gini coefficient
        return compute_gini(n)
    elif return_type == "table":
        # Create and return a table of cumulative population and value shares
        population_shares = np.arange(0, 1.1, 0.1)
        return pd.DataFrame({
            'population_share': population_shares,
            'value_share': [get_value_proportion(lorenz_df, x) for x in population_shares]
        })
    elif return_type == "plot":
        # Plot the Lorenz curve and display the Gini coefficient
        gini_coef = compute_gini(n)
        plt.figure(figsize=(8, 6))
        plt.plot(lorenz_df['cum_population'], lorenz_df['cum_values_prop'], color='#C75B7A')
        plt.plot([0, 1], [0, 1], linestyle='dashed', color='darkgrey')
        plt.title(f"% of population sharing % of {metric}")
        plt.suptitle(f"Lorenz curve for {metric}")
        plt.xlabel("Cumulative Share of Population")
        plt.ylabel("Cumulative Share of Values")
        plt.xlim([0, 1])
        plt.ylim([0, 1])
        plt.grid(True)
        plt.annotate(f"Gini coefficient: {round(gini_coef, 2)}", xy=(0.5, 0.1), xycoords='axes fraction')
        plt.show()
    else:
        raise ValueError("Invalid return type. Choose 'gini', 'table', or 'plot'.")
