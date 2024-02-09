#--------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import math

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
                round(height, rounding) if not percent else f'{height:.{rounding}f}%' if percent else f'{height:.{rounding}f}',
                ha='center', va='bottom',
                color="#FFFFFF" if height > up_break else "#000000", size=10)

    ax.set_xlabel(ylab)
    ax.set_ylabel(xlab)
    ax.set_title(title)

    plt.xticks(rotation=45, ha='right')

    plt.show()


def plot_WOE(IV, predictor):
    # Identify right table
    plot_table = IV['Tables'][predictor]
    
    # Get range
    WOE_values = [table['WOE'] for table in IV['Tables'].values()]
    for i in range(0,len(WOE_values)):
        WOE_range = np.min(WOE_values[i]), np.max(WOE_values[i])
    
    mn=math.floor(np.min(plot_table['WOE']))
    mx=math.ceil(np.max(plot_table['WOE']))
    tick_lst=list(range(mn,mx+1))
    # Plot
    plt.figure(figsize=(12, 8))
    sns.barplot(x=predictor, y='WOE', data=plot_table, color='#8BC7E0')
    for index, value in enumerate(plot_table['WOE']):
        plt.text(index, value, round(value, 1), ha='right', va='top' if value < 0 else 'bottom',color='red' if value < 0 else 'green')
    plt.title(predictor)
    plt.xlabel(predictor)
    plt.ylabel("Weight of Evidence (WOE)")
    plt.ylim(WOE_range[0] * 1.1, WOE_range[1] * 1.1)
    plt.yticks(tick_lst) 
    plt.show()
