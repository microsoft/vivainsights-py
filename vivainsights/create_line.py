# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module visualizes the average of metric by sub-population over time. 
Returns a line plot showing the average of a selected metric by default.
Additional options available to return a summary table.
"""
import pandas as pd
import seaborn as sns
import numpy as np
from vivainsights.extract_date_range import extract_date_range
from vivainsights.color_codes import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def create_line_calc(data: pd.DataFrame, metric: str, hrvar: str, mingroup = 5):
    output = data.groupby(['MetricDate', hrvar]).agg(
        metric = (metric, 'mean'),
        n = ('PersonId', 'nunique')
    )
    output = output[output['n'] >= mingroup]
    output = output.reset_index()
    return output

def create_line_viz(data: pd.DataFrame, metric: str, hrvar: str, mingroup = 5):
    # summarised output
    sum_df = create_line_calc(data, metric, hrvar, mingroup)
    sum_df['MetricDate'] = pd.to_datetime(sum_df['MetricDate'], format='%Y-%m-%d')
    
    # Set colours for the plot
    col_highlight = Colors.HIGHLIGHT_NEGATIVE.value
    col_main = Colors.PRIMARY.value

    # Clean labels for plotting
    clean_nm = metric.replace("_", " ")
    cap_str = extract_date_range(sum_df, return_type = 'text')
    sub_str = f'By {hrvar}'

    # Setup plot size.
    fig, ax = plt.subplots(figsize=(7,4))

    sns.lineplot(
        data = sum_df,    
        x = 'MetricDate',
        y = 'metric',
        hue = hrvar,
        ax = ax,
        palette = COLOR_PALLET_ALT_2[0:sum_df[hrvar].nunique()] # count distinct values of hrvar
    )

    # Remove splines. Can be done one at a time or can slice with a list.
    ax.spines[['top','right','left']].set_visible(False)

    # Shrink y-lim to make plot a bit tighter
    ax.set_ylim(0)

    # Reformat x-axis tick labels
    ax.xaxis.set_tick_params(labelsize = 9, rotation=45) # Set tick label size and rotation
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %y'))
    ax.set_xlabel('') # Remove x-axis label

    # Reformat y-axis tick labels
    ax.yaxis.set_major_locator(plt.FixedLocator(np.arange(0, 25, 5)))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}'))

    ax.yaxis.set_tick_params(pad=-2,             # Pad tick labels so they don't go over y-axis
                            labeltop=True,      # Put x-axis labels on top
                            labelbottom=False,  # Set no x-axis labels on bottom
                            bottom=False,       # Set no ticks on bottom
                            labelsize=11)
    # Set title
    ax.text(x=0.12, y=.91, s= clean_nm, transform=fig.transFigure, ha='left', fontsize=13, weight='bold', alpha=.8)

    # Set subtitle
    ax.text(x=0.12, y=.86, s=sub_str, transform=fig.transFigure, ha='left', fontsize=11, alpha=.8)

    # Set source text
    ax.text(x=0.12, y=-0.08, s=cap_str, transform=fig.transFigure, ha='left', fontsize=9, alpha=.7)

    # return the plot object
    return fig
    # fig.show()
    
    """ Legacy ggplot 
    plot = (
        ggplot(sum_df,
               aes(
                   x='MetricDate', y='metric', group=hrvar)
               ) +
        geom_line() +
        facet_wrap(f'~{hrvar}', ncol = 2) +
        labs(
            title = f'{metric}\n\n{cap_str}',
            caption = cap_str,
            y=metric
        ) +
        scale_x_date(date_breaks = "1 month", date_labels =  "%b %Y") +
        theme(axis_text_x=element_text(angle=60, hjust=1))
    )
    
    return plot
    """

def create_line(data: pd.DataFrame, metric: str, hrvar: str, mingroup = 5, return_type: str = 'plot'):
    """
    Args:
        data (df): person query data
        metric (str): name of the metric to be analysed
        hrvar (str): name of the organizational attribute to be used for grouping
        return_type (str, optional): type of output to return. Defaults to "plot".
    Returns:
        _type_: _description_
    """    
    if return_type == "plot":
        out = create_line_viz(data=data, metric=metric, hrvar=hrvar, mingroup=mingroup)
    elif return_type == "table":
        out = create_line_calc(data=data, metric=metric, hrvar=hrvar, mingroup=mingroup)
    else:
        out = "Invalid input. Please check your inputs and try again."
    return out