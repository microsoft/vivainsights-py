# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module visualizes the average of metric by sub-population over time. 
Returns a line plot showing the average of a selected metric by default.
Additional options available to return a summary table.
"""

__all__ = ['create_line_calc', 'create_line_viz', 'create_line']

import pandas as pd
import seaborn as sns
import numpy as np
from vivainsights.extract_date_range import extract_date_range
from vivainsights.color_codes import *
from vivainsights.totals_col import totals_col
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator
from matplotlib.ticker import MaxNLocator, FuncFormatter

# Ignore warnings for cleaner output
warnings.filterwarnings("ignore")


def create_line_calc(data: pd.DataFrame, metric: str, hrvar: str, mingroup = 5):  
    output = data.groupby(['MetricDate', hrvar]).agg(
        metric = (metric, 'mean'),
        n = ('PersonId', 'nunique')
    )
    output = output[output['n'] >= mingroup]
    output = output.reset_index()
    return output


def _add_header_decoration(fig, color='#fe7f4f'):
    """Orange rule + box just BELOW the title (your exact geometry)."""
    line = Line2D([0.01, 1.0], [0.85, 0.85],
                  transform=fig.transFigure, color=color,
                  linewidth=1.2, clip_on=False)
    fig.add_artist(line)

    rect = plt.Rectangle((0.01, 0.85), 0.03, -0.015,
                         transform=fig.transFigure, facecolor=color,
                         clip_on=False, linewidth=0)
    fig.add_artist(rect)


def create_line_viz(data: pd.DataFrame, metric: str, hrvar: str, mingroup = 5, figsize: tuple = None):
    # summarised output
    sum_df = create_line_calc(data, metric, hrvar, mingroup)
    sum_df['MetricDate'] = pd.to_datetime(sum_df['MetricDate'], format='%Y-%m-%d', errors='coerce')
    sum_df = sum_df.dropna(subset=['MetricDate'])
    
    # Set colours for the plot
    col_highlight = Colors.HIGHLIGHT_NEGATIVE.value
    col_main = Colors.PRIMARY.value

    # Clean labels for plotting
    clean_nm = metric.replace("_", " ")
    cap_str = extract_date_range(sum_df, return_type='text')
    sub_str = f'By {hrvar}'

    if (len(data[hrvar].unique()) <= 4):
        fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))

        sns.lineplot(
            data=sum_df,
            x='MetricDate',
            y='metric',
            hue=hrvar,
            ax=ax,
            palette=COLOR_PALLET_ALT_2[0:sum_df[hrvar].nunique()]
        )

        # Remove splines. Can be done one at a time or can slice with a list.
        ax.spines[['top','right','left']].set_visible(False)
        ax.grid(axis='y', alpha=0.15)

        ymin = 0 if sum_df['metric'].min() >= 0 else sum_df['metric'].min()
        ymax = sum_df['metric'].max()
        pad = (ymax - ymin) * 0.10 if ymax > ymin else 1.0
        ax.set_ylim(ymin, ymax + pad)

        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %y'))
        ax.tick_params(axis='x', rotation=45, labelsize=9, bottom=True, top=False,
                       labelbottom=True, labeltop=False)
        ax.set_xlabel('')

        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0f}'))
        ax.tick_params(axis='y', left=True, right=False, labelleft=True, labelright=False,
                       pad=2, labelsize=11)
        ax.set_ylabel(clean_nm)

        # -------- LEGEND: move OUTSIDE on the right (no overlap) --------
        n_groups = int(sum_df[hrvar].nunique())
        ax.legend(
            title=hrvar,
            frameon=False,
            loc='upper left',
            bbox_to_anchor=(1.02, 1.0),   # outside, to the right
            borderaxespad=0.0,
            ncol=1 if n_groups <= 6 else 2,
            handlelength=2.0,
            columnspacing=1.0,
            labelspacing=0.4
        )

        # Titles & caption
        fig.text(0.02, 0.91, clean_nm, ha='left', fontsize=13, weight='bold', alpha=.8)
        fig.text(0.02, 0.86, sub_str,   ha='left', fontsize=11, alpha=.8)
        fig.text(0.12, -0.08, cap_str,  ha='left', fontsize=9,  alpha=.7)

        # Orange rule + box (below the title)
        _add_header_decoration(fig, color=col_highlight)

        # Layout: reserve top for title + rule and right for legend
        fig.subplots_adjust(top=0.80, right=0.80, bottom=0.22, left=0.10)
        return fig

    else: #hrvar has more than 4 distinct values, so we use facet grid

        facet_grid_plot = sns.FacetGrid(data = sum_df,
                    hue = hrvar,
                    col = hrvar,
                    col_wrap=2,
                    height=4,
                    aspect=1
                    )

        facet_grid_plot.map(sns.lineplot,"MetricDate","metric")

        #To add space between the title and subplots
        facet_grid_plot.figure.tight_layout(rect=[0, 0, 1, 0.96])

        # Set title
        facet_grid_plot.figure.text(x=0.07, y=1, s= clean_nm, ha='left', fontsize=13, weight='bold', alpha=.8)

        # Set subtitle
        facet_grid_plot.figure.text(x=0.07, y=.98, s=sub_str, ha='left', fontsize=11, alpha=.8)

        # Set source text
        facet_grid_plot.figure.text(x=0.1, y=-0.08, s=cap_str, ha='left', fontsize=9, alpha=.7)

        # Add orange line and rectangle at the top (matches other visuals)
        facet_grid_plot.figure.lines.append(
            Line2D(
                [0, 0.9], [0.970, 0.970], 
                transform=facet_grid_plot.figure.transFigure,
                color=col_highlight,
                linewidth=0.6,
                clip_on=False
            )
        )

        facet_grid_plot.figure.patches.extend([
                plt.Rectangle(
                    (0, 0.970), 0.05, -0.005, 
                    facecolor=col_highlight,
                    transform=facet_grid_plot.figure.transFigure,
                    clip_on=False,
                    linewidth=0
            )
        ])

        #setting labels
        for ax in facet_grid_plot.axes:
            ax.set_ylabel(clean_nm)
            ax.set_xlabel('')

        #rotating dates on xticklabels for better readability
        for ax in facet_grid_plot.axes.flat:
            if(len(ax.get_xticklabels())>0):
                ax.set_xticklabels(ax.get_xticklabels(),rotation=45)
        
        return facet_grid_plot


def create_line(data: pd.DataFrame, metric: str, hrvar: str, mingroup = 5, return_type: str = 'plot', figsize: tuple = None):
    """
    Name
    ----
    create_line
    
    Description
    -----------
    Provides a week by week view of a selected metric, visualised as line charts.

    Parameters
    ----------
    data : pandas dataframe
        person query data
    metric : str
        name of the metric to be analysed
    hrvar : str
        name of the organizational attribute to be used for grouping
    mingroup : int, optional
        Numeric value setting the privacy threshold / minimum group size, by default 5
    figsize : tuple, optional
        Size of the figure to be plotted, by default None which sets it to (8, 6)
    return_type : str, optional
        type of output to return. Defaults to "plot".
     
    Returns
    -------
    Various
        The output, either a plot or a table, depending on the value passed to `return_type`.

    Example
    -------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> # Return plot
    >>> create_line(pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation")
    >>> # Return table
    >>> create_line(pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation", return_type = "table")
    """    
    
    ## Handling None value passed to hrvar
    if(hrvar is None):
        data = totals_col(data = data)
        hrvar = "Total"
        
    if return_type == "plot":
        out = create_line_viz(data=data, metric=metric, hrvar=hrvar, mingroup=mingroup, figsize=figsize)
    elif return_type == "table":
        out = create_line_calc(data=data, metric=metric, hrvar=hrvar, mingroup=mingroup)
    else:
        out = "Invalid input. Please check your inputs and try again."
    return out