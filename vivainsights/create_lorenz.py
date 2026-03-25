# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Calculate the Gini coefficient and plot the Lorenz curve for a given metric.
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
    """Look up the cumulative value share for a given population share.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing ``cum_population`` and ``cum_values_prop``
        columns (as produced by ``create_lorenz``).
    population_share : float
        Cumulative population share, between 0 and 1.

    Returns
    -------
    float
        The cumulative value proportion at the given population share.

    Raises
    ------
    ValueError
        If *population_share* is not between 0 and 1.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> lorenz_table = vi.create_lorenz(data=pq_data, metric="Emails_sent", return_type="table")
    >>> vi.get_value_proportion(lorenz_table, population_share=0.5)
    """
    if population_share < 0 or population_share > 1:
        raise ValueError("Population share must be between 0 and 1")

    # Find the row in the DataFrame where the cumulative population meets or exceeds the input share
    closest_row = df[df['cum_population'] >= population_share].iloc[0]
    return closest_row['cum_values_prop']

def compute_gini(x):
    """Compute the Gini coefficient for a numeric vector.

    The Gini coefficient is a measure of statistical dispersion used to
    represent inequality in a distribution.

    Parameters
    ----------
    x : list, numpy.ndarray, or pandas.Series
        Numeric values (e.g. hours, emails sent).

    Returns
    -------
    float
        The Gini coefficient.

    Raises
    ------
    ValueError
        If *x* is not a numeric vector.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.compute_gini(pq_data["Emails_sent"])
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
    """Calculate the Lorenz curve and Gini coefficient for a metric.

    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame containing the data to analyse.
    metric : str
        Column name of the numeric values to analyse.
    return_type : str, default "plot"
        ``"plot"`` to display a Lorenz curve, ``"gini"`` to return the Gini
        coefficient, or ``"table"`` for a DataFrame of cumulative shares.
    figsize : tuple of float or None, default None
        Figure size ``(width, height)`` in inches.  Defaults to ``(8, 6)``.

    Returns
    -------
    matplotlib.figure.Figure, float, or pandas.DataFrame
        The Lorenz curve figure, the Gini coefficient, or a table of
        cumulative population and value shares.

    Raises
    ------
    ValueError
        If *metric* is not in the DataFrame or *return_type* is invalid.

    Examples
    --------
    Compute the Gini coefficient:

    >>> import vivainsights as vi
    >>> vi.create_lorenz(data=vi.load_pq_data(), metric="Emails_sent", return_type="gini")

    Display the Lorenz curve plot:

    >>> vi.create_lorenz(data=vi.load_pq_data(), metric="Emails_sent", return_type="plot")

    Return a table of cumulative population and value shares:

    >>> vi.create_lorenz(data=vi.load_pq_data(), metric="Emails_sent", return_type="table")

    Customize the figure size:

    >>> vi.create_lorenz(
    ...     data=vi.load_pq_data(),
    ...     metric="Collaboration_hours",
    ...     return_type="plot",
    ...     figsize=(10, 8),
    ... )
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