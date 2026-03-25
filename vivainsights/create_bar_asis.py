#--------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Create a bar chart with customizable options and no pre-aggregation.
"""

__all__ = ['create_bar_asis']

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def create_bar_asis(data, group_var, bar_var, title=None, subtitle=None, caption=None, ylab=None, xlab=None,
                    percent=False, bar_colour="default", rounding=1):
    """Create a bar chart from pre-aggregated data.

    Unlike ``create_bar``, this function does not perform any
    aggregation and plots the data as-is.

    Parameters
    ----------
    data : pandas.DataFrame
        Pre-aggregated data to plot.
    group_var : str
        Column name for the x-axis categories.
    bar_var : str
        Column name for the y-axis values.
    title : str or None, default None
        Plot title.
    subtitle : str or None, default None
        Plot subtitle.
    caption : str or None, default None
        Plot caption.
    ylab : str or None, default None
        Label for the y-axis.
    xlab : str or None, default None
        Label for the x-axis.
    percent : bool, default False
        Whether to format bar labels as percentages.
    bar_colour : str, default "default"
        Colour preset: ``"default"``, ``"alert"``, or ``"darkblue"``.
    rounding : int, default 1
        Number of decimal places for bar labels.

    Returns
    -------
    None
        Displays the plot.

    Examples
    --------
    Basic bar chart from pre-aggregated data:

    >>> import vivainsights as vi
    >>> import pandas as pd
    >>> df = pd.DataFrame({"Group": ["A", "B", "C"], "Value": [10, 20, 15]})
    >>> vi.create_bar_asis(df, group_var="Group", bar_var="Value")

    Customize title, subtitle, caption, and bar colour:

    >>> vi.create_bar_asis(
    ...     df,
    ...     group_var="Group",
    ...     bar_var="Value",
    ...     title="Custom Title",
    ...     subtitle="Breakdown by Group",
    ...     caption="Source: sample data",
    ...     bar_colour="alert",
    ... )

    Display values as percentages with custom rounding:

    >>> pct = pd.DataFrame({"Team": ["X", "Y"], "Rate": [0.75, 0.62]})
    >>> vi.create_bar_asis(pct, group_var="Team", bar_var="Rate", percent=True, rounding=2)
    """

    # Set default colors if not specified
    if bar_colour == "default":
        bar_colour = "#34b1e2"
    elif bar_colour == "alert":
        bar_colour = "#FE7F4F"
    elif bar_colour == "darkblue":
        bar_colour = "#1d627e"

    # Determine upper limit for text color adjustment
    up_break = data[bar_var].max() * 1.3

    # Create the plot
    fig, ax = plt.subplots()
    bars = ax.bar(data[group_var], data[bar_var], color=bar_colour)

    # Add text labels on the bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2,
                height,
                round(height, rounding) if not percent else f'{height:.{rounding}f}%' if percent else f'{height:.{rounding}f}',
                ha='center', va='bottom',
                color="#FFFFFF" if height > up_break else "#000000", size=10)

    # Set labels and title
    ax.set_xlabel(ylab)
    ax.set_ylabel(xlab)
    ax.set_title(title)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Show the plot
    plt.show()