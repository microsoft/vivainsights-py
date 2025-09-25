# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
The code defines a function `create_bar` that calculates and visualizes the mean of a selected
metric, grouped by a selected HR variable. 

The metrics are first aggregated at a user-level prior to being aggregated at the level of the HR variable. The function `create_bar` returns either a plot object or a table, depending on the value passed to `return_type`. 
"""
import pandas as pd
import seaborn as sns
from vivainsights.extract_date_range import extract_date_range
from vivainsights.us_to_space import us_to_space
from vivainsights.totals_col import totals_col
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
import matplotlib
from matplotlib.lines import Line2D
from vivainsights.color_codes import Colors  # optional, for the orange highlight

    
def create_bar_calc(
    data: pd.DataFrame,
    metric: str,
    hrvar: str, 
    mingroup = 5,
    stats = False
    ):
    """Calculate the mean of a selected metric, grouped by a selected HR variable."""
    data = data.groupby(['PersonId',hrvar])        
    data = data[metric].mean()
    data = data.reset_index()
    output = data.groupby(hrvar).agg(
        metric = (metric, 'mean'),
        n = ('PersonId', 'nunique')
        )
    output = output[output['n'] >= mingroup]
    output = output.rename_axis(hrvar).reset_index()
    output = output.sort_values(by = 'metric', ascending=False)
    
    if stats == True:
        stats_df = data.groupby(hrvar).agg(
            sd = (metric, 'std'),
            median = (metric, 'median'),
            min = (metric, 'min'),
            max = (metric, 'max')
            )
        
        # Join output with stats_df
        output = pd.merge(output, stats_df, on=hrvar, how='outer')
    
    return output

def _add_header_decoration(fig, color=Colors.HIGHLIGHT_NEGATIVE.value):
    """Orange rule + box just BELOW the title."""
    line = Line2D([0.01, 1.0], [0.85, 0.85],
                  transform=fig.transFigure, color=color,
                  linewidth=1.2, clip_on=False)
    fig.add_artist(line)

    rect = plt.Rectangle((0.01, 0.85), 0.03, -0.015,
                         transform=fig.transFigure, facecolor=color,
                         clip_on=False, linewidth=0)
    fig.add_artist(rect)


def create_bar_viz(
    data: pd.DataFrame,
    metric: str,
    hrvar: str,
    mingroup = 5,
    percent: bool = False,
    plot_title = None,
    plot_subtitle = None,
    figsize: tuple = None):
    """Visualise the mean of a selected metric, grouped by a selected HR variable."""
    sum_df = create_bar_calc(data, metric, hrvar, mingroup)
    caption_text = extract_date_range(data, return_type='text')
    plot_order = sum_df[hrvar].to_numpy()

    # Title and subtitle text
    if plot_title is None:
        title_text = us_to_space(metric)
    else:
        title_text = plot_title

    if plot_subtitle is None:
        subtitle_text = f'Weekly average by {hrvar}'  # TODO: make this dynamic by date interval
    else:
        subtitle_text = plot_subtitle

    # fig = plt.figure()
    fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))

    # Create grid
    # Zorder tells it which layer to put it on. We are setting this to 1 and our data to 2 so the grid is behind the data.
    ax.grid(which="major", axis='x', color='#758D99', alpha=0.6, zorder=1)

    # Remove splines. Can be done 1 at a time or can slice with a list.
    ax.spines[['top', 'right', 'bottom']].set_visible(False)

    # Make left spine slightly thicker
    ax.spines['left'].set_linewidth(1.1)

    ax.barh(sum_df[hrvar], sum_df['metric'], color='#1d627e', zorder=2)

    if percent == True:
        # Set the x-axis format to percentage
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

    # Shrink y-lim to make plot a bit tighter
    # Using length of summary table to make it dynamic
    ax.set_ylim(-0.5, len(sum_df) - 0.5)

    # Reformat x-axis tick labels
    ax.xaxis.set_tick_params(labeltop=True,  # Put x-axis labels on top
                             labelbottom=False,  # Set no x-axis labels on bottom
                             bottom=False,  # Set no ticks on bottom
                             labelsize=9,  # Set tick label size
                             pad=-1)  # Lower tick labels a bit

    ax.yaxis.set_tick_params(pad=10,  # Pad tick labels so they don't go over y-axis
                             labelsize=9,  # Set label size
                             bottom=False)  # Set no ticks on bottom/left

    # Reformat y-axis tick labels
    ax.set_yticks(range(len(sum_df)))
    ax.set_yticklabels(sum_df[hrvar], ha='right')

    # Titles & caption (figure-level, consistent with create_line)
    fig.text(0.02, 0.91, title_text,   ha='left', fontsize=13, weight='bold', alpha=.8)
    fig.text(0.02, 0.86, subtitle_text,ha='left', fontsize=11, alpha=.8)
    fig.text(0.12, 0.02, caption_text,ha='left', va='bottom', fontsize=9,  alpha=.7)

    # Orange rule + box (below title), consistent with create_line
    _add_header_decoration(fig)
    # Layout: reserve top for title/rule and bottom for caption
    fig.subplots_adjust(top=0.80, right=0.95, bottom=0.12, left=0.10)


    if percent == True:
        ax.bar_label(ax.containers[0], labels=[f"{100 * value:.0f}%" for value in sum_df['metric']], label_type="edge",
                     padding=3)
    else:
        ax.bar_label(ax.containers[0], fmt='%.0f', label_type='edge', padding=3)  # annotate

    ax.margins(y=0.05)  # pad the spacing between the number and the edge of the figure

    # return the plot object
    return fig    

def create_bar(
    data: pd.DataFrame,
    metric: str,
    hrvar: str,
    mingroup: int = 5,
    percent: bool = False,
    return_type: str = "plot",
    plot_title = None,
    plot_subtitle = None,
    figsize: tuple = None
    ):
    """
    Name
    -----
    create_bar 
    
    Description
    -----------
    The function `create_bar` calculates and visualizes the mean of a selected metric, grouped by a selected HR variable. 
    The metrics are first aggregated at a user-level prior to being aggregated at the level of the HR variable. 
    `create_bar` returns either a plot object or a table, depending on the value passed to `return_type`.
    Internally, `create_bar` calls `create_bar_viz()` and `create_bar_calc()` to create the plot and calculate the mean of the selected metric, respectively.

    Parameters
    ----------
    data : pd.DataFrame
        Person query data.
    metric : str
        Name of the metric to be analysed.
    hrvar : str
        Name of the organizational attribute to be used for grouping.
    mingroup : int, optional
        Minimum group size. Defaults to 5.
    percent : bool, optional
        Whether to display values as percentages. Defaults to False.
    return_type : str, optional
        The type of output to return. Can be "plot" or "table". Defaults to "plot".
    plot_title : str, optional
        Title of the plot. Defaults to None.
    plot_subtitle : str, optional
        Subtitle of the plot. Defaults to None.
    figsize : tuple, optional
        The `figsize` parameter is an optional tuple that specifies the size of the figure for the boxplot visualization. It should be in the format `(width, height)`, where `width` and `height` are in inches. If not provided, a default size of (8, 6) will be used.

    Returns
    -------
    Various
        The output, either a plot or a table, depending on the value passed to `return_type`.

    Example
    -------
    >>> create_bar(pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation")
    """  
    
    ## Handling None value passed to hrvar
    if(hrvar is None):
        data = totals_col(data)
        hrvar = "Total"
        
    if return_type == "plot":
        out = create_bar_viz(data=data, metric=metric, hrvar=hrvar, percent=percent, mingroup=mingroup, plot_title = plot_title, plot_subtitle = plot_subtitle,figsize=figsize)
    elif return_type == "table":
        out = create_bar_calc(data=data, metric=metric, hrvar=hrvar, mingroup=mingroup)
    else:
        out = "Invalid input. Please check your inputs and try again."
    return out