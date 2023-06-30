# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""_summary_
This module performs a rank operation on all groups across HR attributes for a selected Viva Insights metric.
"""
import pandas as pd
from vivainsights.create_bar import create_bar_calc
from vivainsights.extract_date_range import extract_date_range
import matplotlib.pyplot as plt
from vivainsights.us_to_space import us_to_space

def create_rank_calc(data: pd.DataFrame,
                     metric: str,
                     hrvar = ['Organization', 'FunctionType'],
                     mingroup = 5):
    
    output_list = [] # create an empty list to store the outputs
    
    for i in hrvar:             
        ind_df = create_bar_calc(data = data, metric = metric, hrvar = i) # individual data frames per hrvar
        ind_df = ind_df.rename(columns = {i: 'attributes'}) # rename the hrvar column to 'attributes'
        ind_df['hrvar'] = i # add a column with the name of the hrvar
        ind_df = ind_df[['hrvar', 'attributes', 'metric', 'n']] # reorder the columns
        output_list.append(ind_df) # appending output to the list
        output = pd.concat(output_list, axis=0) # binding the data together
    output = output[output['n'] >= mingroup] # filtering out groups with less than mingroup
    output = output.sort_values(by = 'metric', ascending=False)
    return output

def create_rank_viz(data: pd.DataFrame,
                    metric,
                    hrvar = ['Organization', 'FunctionType', 'LevelDesignation', 'SupervisorIndicator'],
                    mingroup = 5):
    
    cap_str = extract_date_range(data, return_type = 'text')
    col_highlight = '#fe7f4f'
    col_main = '#1d627e'
    
    result_list = []
    for i in hrvar:
        sum_df = create_rank_calc(data, metric, hrvar, mingroup) # summarised output with columns 'hrvar', 'attributes', 'metric', 'n'
        sum_df_top = sum_df[sum_df['hrvar'] == i].head(1) # top 1 row of the summarised output matching the hrvar            
        sum_df_bot = sum_df[sum_df['hrvar'] == i].tail(1) # bottom 1 row of the summarised output matching the hrvar
        sum_df_top['type'] = 'max'
        sum_df_bot['type'] = 'min'
        result_list.append(sum_df_top)
        result_list.append(sum_df_bot)
        
    result = pd.concat(result_list, axis=0)
    result_pivot = result.pivot(index='hrvar', columns='type', values=['attributes','metric'])    
    result_pivot.columns = ["_".join(a) for a in result_pivot.columns.to_flat_index()]   
    result_pivot = result_pivot.reset_index()
    
    # Setup plot size.
    fig, ax = plt.subplots(figsize=(7,4))
    
    # Create grid 
    # Zorder tells it which layer to put it on. We are setting this to 1 and our data to 2 so the grid is behind the data.
    ax.grid(which="major", axis='both', color='#758D99', alpha=0.6, zorder=1)
    
    # Remove splines. Can be done one at a time or can slice with a list.
    ax.spines[['top','right','bottom']].set_visible(False)
    
    # Plot data
    # Plot horizontal lines first
    ax.hlines(
        y=result_pivot['hrvar'],
        xmin=result_pivot['metric_min'],
        xmax=result_pivot['metric_max'],
        color='#758D99',
        zorder=2, linewidth=2, label='_nolegend_', alpha=.8
        )
    
    # Plot bubbles next
    ax.scatter(result_pivot['metric_min'], result_pivot['hrvar'], label='1960', s=60, color='#DB444B', zorder=3)
    ax.scatter(result_pivot['metric_max'], result_pivot['hrvar'], label='2020', s=60, color= col_main, zorder=3)
    
    # Set xlim
    ax.set_xlim(0, 1.1*result_pivot['metric_max'].max())
       
    # Reformat x-axis tick labels
    ax.xaxis.set_tick_params(labeltop=True,      # Put x-axis labels on top
                            labelbottom=False,  # Set no x-axis labels on bottom
                            bottom=False,       # Set no ticks on bottom
                            labelsize=9,       # Set tick label size
                            pad=-1)             # Lower tick labels a bit
    
    ax.yaxis.set_tick_params(pad = 10, labelsize = 9, bottom = False) # no ticks on bottom
    ax.set_yticklabels(result_pivot['hrvar'], ha = 'right', fontsize=9) # Set y-axis tick labels, align right
    
    ax.legend(['min', 'max'],
              loc = (-.29, 1.09),
              ncol = 2,
              frameon = False,
              handletextpad = -.1,
              handleheight = 1)
    
    # Add in line and tag
    ax.plot(
        [-0.08, .9], # Set width of line
        [1.17, 1.17], # Set height of line
        transform = fig.transFigure, # Set location relative to plot
        clip_on = False,
        color = col_highlight,
        linewidth = .6
    )
    
    ax.add_patch(
        plt.Rectangle(
            (-0.08, 1.17),
            0.05,
            -0.025,
            facecolor = col_highlight,
            transform = fig.transFigure,
            clip_on = False,
            linewidth = 0
            )
    )
    
    # Set title
    ax.text(
        x = -0.08, y = 1.09,
        s = us_to_space(metric),
        transform = fig.transFigure,
        ha = 'left',
        fontsize = 13,
        weight = 'bold',
        alpha = .8
    )
    
    # Set subtitle
    ax.text(
        x = -0.08, y = 1.04,
        s = 'By organizational attributes',
        transform = fig.transFigure,
        ha = 'left',
        fontsize = 11,        
        alpha = .8
    )
    
    # Set caption
    ax.text(x = -0.08, y = 0.04, s = cap_str, transform = fig.transFigure, ha = 'left', fontsize = 9, alpha = .7)
    
    # return the plot object
    return fig


def create_rank(data: pd.DataFrame, metric: str, hrvar: str, mingroup = 5, return_type: str = "plot"):
    """_summary_
    Args:
        data (df): person query data
        metric (str): name of the metric to be analysed
        hrvar (str): name(s) of the organizational attribute(s) to be used for grouping
        return_type (str, optional): type of output to return. Defaults to "plot".
    Returns:
        _type_: _description_
    """
    if return_type == "plot":
        out = create_rank_viz(data=data, metric=metric, hrvar=hrvar, mingroup=mingroup)
    elif return_type == "table":
        out = create_rank_calc(data=data, metric=metric, hrvar=hrvar, mingroup=mingroup)
    else:
        out = "Invalid input. Please check your inputs and try again."
    return out
    