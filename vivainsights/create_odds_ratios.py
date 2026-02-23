# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Calculate odds ratios for ordinal metrics against a specified outcome.
"""

__all__ = ['create_odds_ratios', 'compute_fav']

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def create_odds_ratios(data: pd.DataFrame, ord_metrics: list, metric: str, return_type: str = 'table'):
    """
    Calculate odds ratios for ordinal metrics against a specified metric.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.
    ord_metrics : list of str
        Column names of the ordinal variables.
    metric : str
        Variable to calculate proportional odds against ``ord_metrics``.
    return_type : str, optional
        ``"table"`` (default) returns the odds-ratio DataFrame;
        ``"plot"`` returns a bar chart.

    Returns
    -------
    pandas.DataFrame or matplotlib.figure.Figure
        Odds-ratio table or visualization depending on ``return_type``.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.create_odds_ratios(
    ...     data=pq_data,
    ...     ord_metrics=["Engagement_Score", "Satisfaction_Score"],
    ...     metric="Copilot_Usage",
    ...     return_type="table",
    ... )
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
        contingency_table = pd.crosstab(data[metric], data[ord_metric])
        
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

        # --- Add n: count of distinct PersonId for each (metric, Level, Ordinal_Metric) ---
        # Determine PersonId column
        person_id_col = "PersonId" if "PersonId" in data.columns else data.columns[0]
        # Compute counts
        n_counts = (
            data
            .assign(Level=data[ord_metric], Ordinal_Metric=ord_metric)
            .groupby([metric, "Level", "Ordinal_Metric"])[person_id_col]
            .nunique()
            .reset_index(name="n")
        )
        # Merge counts into odds_ratios_all_levels
        odds_ratios_all_levels = odds_ratios_all_levels.merge(
            n_counts, how="left", on=[metric, "Level", "Ordinal_Metric"]
        )

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
    Convert ordinal variables into categorical favorable/unfavorable scores.

    Parameters
    ----------
    data : pandas.DataFrame
        Dataset containing the ordinal variables.
    ord_metrics : list of str
        Column names of the ordinal variables.
    item_options : int, optional
        Number of scale points in the ordinal metrics. Defaults to 5.
    fav_threshold : int, optional
        Threshold on a 100-point scale above which a score is favourable.
        Defaults to 70.
    unfav_threshold : int, optional
        Threshold on a 100-point scale below which a score is unfavourable.
        Defaults to 40.
    drop_neutral : bool, optional
        Whether to drop neutral scores. Defaults to ``True``.

    Returns
    -------
    pandas.DataFrame
        Input DataFrame with added ``<metric>_100`` and ``<metric>_fav``
        columns. If ``drop_neutral`` is ``True``, rows with neutral scores
        are removed.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.compute_fav(
    ...     data=pq_data,
    ...     ord_metrics=["eSat", "Initiative"],
    ...     item_options=5,
    ...     fav_threshold=70,
    ...     unfav_threshold=40,
    ...     drop_neutral=True,
    ... )
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
