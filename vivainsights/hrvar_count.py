# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module generates a count of the distinct persons in the data population.
Returns a bar plot of the counts by default, with an option to return a summary table.
"""
import pandas as pd
import matplotlib.pyplot as plt
from vivainsights.extract_date_range import extract_date_range

def hrvar_count_calc(data: pd.DataFrame, hrvar: str):
    """Calculate the number of distinct persons in the data population, grouped by a selected HR variable."""
    data = data.groupby([hrvar])
    data = data['PersonId'].nunique().reset_index(name='n')
    output = data.sort_values(by = 'n', ascending=False)
    return output

def hrvar_count_viz(data: pd.DataFrame, hrvar: str):
    """Visualise the number of distinct persons in the data population, grouped by a selected HR variable."""
    sum_df = hrvar_count_calc(data = data, hrvar = hrvar)
    cap_str = extract_date_range(data, return_type = 'text')
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create grid 
    # Zorder tells it which layer to put it on. We are setting this to 1 and our data to 2 so the grid is behind the data.
    ax.grid(which="major", axis='x', color='#758D99', alpha=0.6, zorder=1)
    
    # Remove splines. Can be done one at a time or can slice with a list.
    ax.spines[['top','right','bottom']].set_visible(False)
    
    # Make left spine slightly thicker
    ax.spines['left'].set_linewidth(1.1)
    
    # Create bar plot
    ax.barh(sum_df[hrvar], sum_df['n'], color='#1d627e', zorder=2)
    
    # Shrink y-lim to make plot a bit tighter
    # Using length of summary table to make it dynamic
    ax.set_ylim(-0.5, len(sum_df)-0.5)
    
    # Reformat x-axis tick labels
    ax.xaxis.set_tick_params(
        labeltop=True,      # Put x-axis labels on top
        labelbottom=False,  # Set no x-axis labels on bottom
        bottom=False,       # Set no ticks on bottom
        labelsize=9,       # Set tick label size
        pad=-1          # Lower tick labels a bit
        )
    # Reformat y-axis tick labels
    ax.yaxis.set_tick_params(
        pad=10,      # Pad tick labels so they don't go over y-axis
        labelsize=9,  # Set label size
        bottom=False  # Set no ticks on bottom/left
        )  
    
    # Reformat y-axis tick labels
    ax.set_yticks(range(len(sum_df)))
    ax.set_yticklabels(
        sum_df[hrvar],   # Set labels again
        ha = 'right'      # Set horizontal alignment to right
        ) 
    
    # Add in line and tag
    ax.plot([-.35, .87],                 # Set width of line
            [1.02, 1.02],                # Set height of line
            transform=fig.transFigure,   # Set location relative to plot
            clip_on=False, 
            color='#fe7f4f', 
            linewidth=.6)
    
    ax.add_patch(plt.Rectangle((-.35,1.02),             # Set location of rectangle by lower left corder
                            0.12,                       # Width of rectangle
                            -0.02,                      # Height of rectangle. Negative so it goes down.
                            facecolor='#fe7f4f', 
                            transform=fig.transFigure, 
                            clip_on=False, 
                            linewidth = 0))
    
    # Add in title, subtitle, and caption
    ax.text(x=-.35, y=.96, s= f'People by {hrvar}', transform=fig.transFigure, ha='left', fontsize=13, weight='bold', alpha=.8)
    # ax.text(x=-.35, y=.925, s= sub_title, transform=fig.transFigure, ha='left', fontsize=11, alpha=.8)    
    ax.text(x=-.35, y=.08, s=cap_str, transform=fig.transFigure, ha='left', fontsize=9, alpha=.7)
    
    plt.bar_label(ax.containers[0], fmt = '%.0f', label_type='edge', padding = 3) # annotate
    plt.margins(y=0.3) # pad the spacing between the number and the edge of the figure  
    
    # return the plot object
    return fig

def hrvar_count(data: pd.DataFrame, hrvar: str = 'Organization', return_type: str = "plot"):
    """
    Name
    ----
    hrvar_count

    Description
    -----------
    This function generates a count of the distinct persons in the data population, grouped by a selected HR variable.

    Parameters
    ---------
    data : ppandas dataframe
        person query data
    hrvar : str
         name of the organizational attribute to be used for grouping
    return_type : str or optional 
        type of output to return. Defaults to "plot".

    Example
    -------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.hrvar_count(pq_data, hrvar = "LevelDesignation")
    """
    if return_type == "plot":
        out = hrvar_count_viz(data=data, hrvar=hrvar)
    elif return_type == "table":
        out = hrvar_count_calc(data=data, hrvar=hrvar)
    else:
        out = "Invalid input. Please check your inputs and try again."
    return out