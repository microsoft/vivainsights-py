#--------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

__all__ = ['create_bar_asis']

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def create_bar_asis(data, group_var, bar_var, title=None, subtitle=None, caption=None, ylab=None, xlab=None,
                    percent=False, bar_colour="default", rounding=1):
    """
    Create a bar chart with customizable options.

    Parameters:
        - data: DataFrame, the data to be plotted.
        - group_var: str, the variable to be grouped by on the x-axis.
        - bar_var: str, the variable to be plotted on the y-axis.
        - title: str, optional, title of the plot.
        - subtitle: str, optional, subtitle of the plot.
        - caption: str, optional, caption of the plot.
        - ylab: str, optional, label for the y-axis.
        - xlab: str, optional, label for the x-axis.
        - percent: bool, optional, whether to display values as percentages.
        - bar_colour: str, optional, color of the bars. Available options: "default", "alert", "darkblue".
        - rounding: int, optional, number of decimal places to round the values.

    Returns:
        - None: Displays the plot.

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