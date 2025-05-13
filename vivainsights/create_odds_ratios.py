# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module calculates odds ratios for ordinal metrics against a specified metric.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_odds_ratios(data: pd.DataFrame, ord_metrics: list, metric: str, return_type: str = 'table'):
    """
    Name
    ----
    create_odds_ratios

    Description
    -----------
    Calculates odds ratios for ordinal metrics against a specified metric.

    Parameters
    ----------
    data : pandas dataframe
        A Person Query dataset in the form of a pandas DataFrame.
    ord_metrics : list
        List of strings referring to the column names of the ordinal variables.
    metric : str
        Name of the variable to calculate proportional odds against the `ord_metrics`.
    return_type : str, optional
        Specifies what to return. Defaults to 'table'. 
        - 'table': Returns a data frame with the final odds ratio table sorted by odds ratio.
        - 'plot': Returns a plot for visualizing the odds ratio.

    Returns
    -------
    pandas DataFrame or matplotlib Figure
        Depending on the value of `return_type`, either a table or a plot is returned.

    Example
    -------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.create_odds_ratios(data=pq_data, ord_metrics=["Engagement_Score", "Satisfaction_Score"], metric="Copilot_Usage", return_type="table")
    """
    # Validate inputs
    if not isinstance(ord_metrics, list):
        raise ValueError("`ord_metrics` must be a list of column names.")
    if metric not in data.columns:
        raise ValueError(f"Metric '{metric}' not found in data.")
    for ord_metric in ord_metrics:
        if ord_metric not in data.columns:
            raise ValueError(f"Ordinal metric '{ord_metric}' not found in data.")

    # Initialize a list to store odds ratio results
    odds_ratios = []

    # Calculate odds ratios for each ordinal metric
    for ord_metric in ord_metrics:
        # Create a contingency table
        contingency_table = pd.crosstab(data[metric], data[f"{ord_metric}_100"])
        
        # Add 0.5 to each cell to avoid division by zero
        contingency_table += 0.5

        # Calculate odds for each level of the ordinal metric
        odds = contingency_table.div(contingency_table.sum(axis=1), axis=0)

        # Calculate odds ratios for all levels
        odds_ratios_all_levels = odds.div(odds.iloc[:, 0], axis=0)

        # Reshape odds_ratios_all_levels for inclusion in the output
        odds_ratios_all_levels = odds_ratios_all_levels.reset_index().melt(
            id_vars=[metric], var_name="Level", value_name="Odds_Ratio"
        )
        odds_ratios_all_levels["Ordinal_Metric"] = ord_metric

        # Append to the results
        odds_ratios.append(odds_ratios_all_levels)

    # Combine all results into a single DataFrame
    odds_ratios_df = pd.concat(odds_ratios, ignore_index=True)

    if return_type == "table":
        return odds_ratios_df
    elif return_type == "plot":
        # Create a bar plot for visualizing odds ratios
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=odds_ratios_df, x="Odds_Ratio", y="Ordinal_Metric", hue="Level", ax=ax, palette="Blues_d")
        ax.set_title("Odds Ratios for Ordinal Metrics")
        ax.set_xlabel("Odds Ratio")
        ax.set_ylabel("Ordinal Metric")
        return fig
    else:
        raise ValueError("Invalid `return_type`. Choose 'table' or 'plot'.")

def compute_fav(data: pd.DataFrame, ord_metrics: list, item_options: int = 5, fav_threshold: int = 70, unfav_threshold: int = 40, drop_neutral: bool = True):
    """
    Name
    ----
    compute_fav

    Description
    -----------
    Converts ordinal variables into categorical variables with favorable and unfavorable scores.

    Parameters
    ----------
    data : pandas dataframe
        A dataset containing the ordinal variables.
    ord_metrics : list
        List of strings referring to the column names of the ordinal variables.
    item_options : int, optional
        Number of options in the ordinal metrics. Default is 5.
    fav_threshold : int, optional
        Threshold for favorable scores (in 100-point scale). Default is 70.
    unfav_threshold : int, optional
        Threshold for unfavorable scores (in 100-point scale). Default is 40.
    drop_neutral : bool, optional
        Whether to drop neutral scores. Default is True.

    Returns
    -------
    pandas DataFrame
        A DataFrame with the ordinal variables converted into categorical variables.

    Example
    -------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.compute_fav(data=pq_data, ord_metrics=["eSat", "Initiative"], item_options=5, fav_threshold=70, unfav_threshold=40, drop_neutral=True)
    """
    # Validate inputs
    if not isinstance(ord_metrics, list):
        raise ValueError("`ord_metrics` must be a list of column names.")
    for ord_metric in ord_metrics:
        if ord_metric not in data.columns:
            raise ValueError(f"Ordinal metric '{ord_metric}' not found in data.")

    # Convert ordinal metrics to a 100-point scale and categorize into favorability
    for ord_metric in ord_metrics:
        data[f"{ord_metric}_100"] = (data[ord_metric] - 1) * (100 / (item_options - 1))
        data[f"{ord_metric}_fav"] = data[f"{ord_metric}_100"].apply(
            lambda x: 'fav' if x > fav_threshold else ('unfav' if x < unfav_threshold else 'neu')
        )
        if drop_neutral:
            data = data[data[f"{ord_metric}_fav"] != 'neu']

    return data
