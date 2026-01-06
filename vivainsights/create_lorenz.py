# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module calculates the Gini coefficient and plots the Lorenz curve for a given metric.
"""

__all__ = ['get_value_proportion', 'compute_gini', 'create_lorenz']

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple

from matplotlib.lines import Line2D

# Try vivainsights color, fall back to the hex
try:
    from vivainsights.color_codes import Colors
    _HIGHLIGHT = Colors.HIGHLIGHT_NEGATIVE.value
except Exception:
    _HIGHLIGHT = "#fe7f4f"

# Header layout constants
_TITLE_Y   = 0.955
_SUB_Y     = 0.915
_RULE_Y    = 0.900
_TOP_LIMIT = 0.84   # push axes down to leave room for header

def _retitle_left(fig, title_text, subtitle_text=None, left=0.01):
    """Left-aligned figure-level title/subtitle; hide any axes/supertitle."""
    # Remove any axes titles and a prior suptitle
    for ax in fig.get_axes():
        try: ax.set_title("")
        except Exception: pass
    if getattr(fig, "_suptitle", None) is not None:
        fig._suptitle.set_visible(False)

    fig.text(left, _TITLE_Y, title_text, ha="left", fontsize=13, weight="bold", alpha=.8)
    if subtitle_text:
        fig.text(left, _SUB_Y, subtitle_text, ha="left", fontsize=11, alpha=.8)

def _add_header_decoration(fig, color=_HIGHLIGHT, y=_RULE_Y):
    """Orange rule + small box under the subtitle, drawn on a top overlay."""
    overlay = fig.add_axes([0, 0, 1, 1], frameon=False, zorder=10)
    overlay.set_axis_off()
    overlay.add_line(Line2D([0.01, 1.0], [y, y], transform=overlay.transAxes,
                            color=color, linewidth=1.2))
    overlay.add_patch(plt.Rectangle((0.01, y), 0.03, -0.015,
                                    transform=overlay.transAxes,
                                    facecolor=color, linewidth=0))

def _reserve_header_space(fig, top=_TOP_LIMIT):
    """Move the plot area down so it doesn't overlap the header."""
    try:
        if hasattr(fig, "get_constrained_layout") and fig.get_constrained_layout():
            fig.set_constrained_layout(False)
    except Exception:
        pass
    fig.subplots_adjust(top=top)


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
    Description
    -----------
    Compute the Gini coefficient, a measure of statistical dispersion to represent inequality.

    Parameters
    ----------
    x (list, np.ndarray, pd.Series): A numeric vector representing values (e.g., income, emails sent).

    Returns
    -------
    float: The Gini coefficient for the given vector of values.

    Raises
    ------
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

def create_lorenz(data, metric, return_type="plot",figsize: Optional[Tuple[float, float]] = None ):
    """
    Name
    ----
    create_lorenz
    
    Description
    -----------
    Calculate and return the Lorenz curve and Gini coefficient for a given metric.

    Parameters
    ----------
    data (pd.DataFrame): DataFrame containing the data to analyze.
    metric (str): The column name in the DataFrame representing the values to analyze.
    return_type (str): The type of output to return: 
                       - "gini": returns the Gini coefficient.
                       - "table": returns a DataFrame of cumulative population and value shares.
                       - "plot" (default): displays a Lorenz curve plot with the Gini coefficient.

    Returns
    -------
    float/pd.DataFrame/None: Depending on return_type:
                             - "gini": returns the Gini coefficient.
                             - "table": returns a DataFrame of population and value shares.
                             - "plot": displays the Lorenz curve plot

    Raises
    ------
    ValueError: If the metric is not found in the DataFrame, or if an invalid return_type is specified.
    
    
    Examples
    --------
    Using `pq_data` from `vi.load_pq_data()`, which returns a DataFrame with an "Emails_sent" column.
    
    >>> import vivainsights as vi
    >>> # Compute the Gini coefficient:
    >>> vi.create_lorenz(data=vi.load_pq_data(), metric="Emails_sent", return_type="gini")

    >>> # Compute the underlying table for the Lorenz curve:
    >>> vi.create_lorenz(data=vi.load_pq_data(), metric="Emails_sent", return_type="table")
    
    >>> # Plot the Lorenz curve
    >>> vi.create_lorenz(data=vi.load_pq_data(), metric="Emails_sent", return_type="plot")
    
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

    if return_type == "plot":
        gini_coef = compute_gini(n)
        fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))

        # Lorenz curve + equality line
        ax.plot(lorenz_df['cum_population'], lorenz_df['cum_values_prop'], color='#C75B7A')
        ax.plot([0, 1], [0, 1], linestyle='dashed', color='darkgrey')

        # Axes labels and limits
        ax.set_xlabel("Cumulative Share of Population")
        ax.set_ylabel("Cumulative Share of Values")
        ax.set_xlim([0, 1]); ax.set_ylim([0, 1])
        ax.grid(True)

        # Gini annotation inside axes
        ax.annotate(f"Gini coefficient: {round(gini_coef, 2)}",
                    xy=(0.5, 0.1), xycoords='axes fraction')

        # --- Header (figure-level, left-aligned) + orange rule/box ---
        title    = f"Lorenz curve for {metric}"
        subtitle = f"% of population sharing % of {metric}"
        _retitle_left(fig, title, subtitle, left=0.01)
        _add_header_decoration(fig)     # draws at _RULE_Y below subtitle
        _reserve_header_space(fig)      # shifts Axes down; avoids overlap

        return fig
      
    elif return_type == "gini":
        # Return the Gini coefficient
        return compute_gini(n)
    elif return_type == "table":
        # Create and return a table of cumulative population and value shares
        population_shares = np.arange(0, 1.1, 0.1)
        return pd.DataFrame({
            'population_share': population_shares,
            'value_share': [get_value_proportion(lorenz_df, x) for x in population_shares]
        })
    else:
        raise ValueError("Invalid return type. Choose 'gini', 'table', or 'plot'.")