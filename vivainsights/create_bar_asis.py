# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def create_bar_asis(data, group_var, bar_var, title=None, subtitle=None, caption=None, ylab=None, xlab=None,
                    percent=False, bar_colour="default", rounding=1):

    if bar_colour == "default":
        bar_colour = "#34b1e2"
    elif bar_colour == "alert":
        bar_colour = "#FE7F4F"
    elif bar_colour == "darkblue":
        bar_colour = "#1d627e"

    up_break = data[bar_var].max() * 1.3

    fig, ax = plt.subplots()
    bars = ax.bar(data[group_var], data[bar_var], color=bar_colour)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2,
                height,
                round(height, rounding) if not percent else f'{height:.{rounding}f}%',
                ha='center', va='bottom',
                color="#FFFFFF", fontweight='bold', size=8)

    # ax.set_ylim(0, up_break)
    ax.set_xlabel(ylab)
    ax.set_ylabel(xlab)
    ax.set_title(title)
    # ax.set_subtitle(subtitle)
    # ax.set_caption(caption)

    plt.xticks(rotation=45, ha='right')

    plt.show()


def plot_WOE(IV, predictor):
    # Identify right table
    plot_table = IV["Tables"][predictor].assign(labelpos=np.where(IV["Tables"][predictor]["WOE"] <= 0, 1.2, -1))

    # Get range
    WOE_range = [IV["Tables"][variable]["WOE"].min() for variable in IV["Summary"]["Variable"]]

    # Plot
    plt.figure()
    sns.barplot(x=predictor, y="WOE", data=plot_table, ci=None, color=sns.color_palette("deep")[0])
    plt.title(predictor)
    plt.xlabel(predictor)
    plt.ylabel("Weight of Evidence (WOE)")
    plt.ylim(WOE_range[0] * 1.1, max(WOE_range) * 1.1)
    plt.show()