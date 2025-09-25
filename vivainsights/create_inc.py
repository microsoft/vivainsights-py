# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module creates an incidence analysis reflecting the proportion of the population scoring above or below a specified threshold for a metric. 
"""
import typing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from vivainsights.color_codes import COLOR_PALLET_ALT_2
from vivainsights.create_bar import create_bar
from vivainsights.extract_date_range import extract_date_range

def create_inc(data: pd.DataFrame, metric: str, hrvar: typing.Union[typing.List, str], mingroup: int = 5, threshold: float = None, position: str = None, return_type: str = 'plot'):
    """
    Name
    ----
    create_inc

    Description
    -----------
    Create an incidence analysis reflecting proportion of population scoring above or below a threshold for a metric. 
    An incidence analysis is generated, with each value in the table reflecting the proportion of the population that 
    is above or below a threshold for a specified metric. There is an option to only provide a single `hrvar` in which a 
    bar plot is generated, or two `hrvar` values where an incidence table (heatmap) is generated.

    Parameters
    ----------
    data : pandas dataframe
        A Standard Person Query dataset in the form of a Pandas DataFrame.
    metric : str 
        Name of the metric, e.g. "Collaboration_hours".
    hrvar : str or list
         Name(s) of the HR Variable(s) by which to split metrics.
    mingroup : int
        Privacy threshold / minimum group size. Defaults to 5.
    threshold : float
        Threshold value to split the data based on the position argument. Defaults to None.
    position :  str 
        One of the below valid values:
        - "above": show incidence of those equal to or above the threshold
        - "below": show incidence of those equal to or below the threshold
    return_type : str
        What to return. This must be one of the following strings:
        - "plot"
        - "table"
                    
    Returns
    -------
    Output is returned depending on the value passed to the return_type argument:
    - "plot": Matplotlib or Seaborn plot object
    - "table": Pandas DataFrame
    
    Raises
    ------
    ValueError: If hrvar is not a string or list with at most length 2.

    Example
    -------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.create_inc(
        pq_data, 
        metric = 'Collaboration_hours',
        hrvar = 'LevelDesignation',
        mingroup = 5,
        threshold = 10,
        position = 'above',
        return_type = 'plot'
        ) 
    """
    
    if not isinstance(hrvar, list):
        hrvar = [hrvar]
    if len(hrvar) > 2:
        raise ValueError("`hrvar` can only accept a list of length 2.")
    
    if len(hrvar) == 1:
        return create_inc_bar(data, metric, hrvar[0], mingroup, threshold, position, return_type)
    else:
        return create_inc_grid(data, metric, hrvar, mingroup, threshold, position, return_type)
    
def create_inc_bar(data: pd.DataFrame, metric: str, hrvar: str, mingroup: int = 5, threshold: float = None, position: str = None, return_type: str='plot',figsize: tuple = None):
    """
    Name
    -----
    create_inc_bar

    Description
    -----------
    Run `create_inc` with only single `hrvar`. Returning a bar chart

    Parameters
    ----------
    data : pandas dataframe
        A Standard Person Query dataset in the form of a Pandas DataFrame.
    metric : str 
        Name of the metric, e.g. "Collaboration_hours".
    hrvar : str
        Name of the HR Variable by which to split metrics.
    mingroup : int
        Privacy threshold / minimum group size. Defaults to 5.
    threshold : float
        Threshold value to split the data based on the position argument. Defaults to None.
    position : str
        One of the below valid values:
        - "above": show incidence of those equal to or above the threshold
        - "below": show incidence of those equal to or below the threshold
    figsize : tuple, optional
        The `figsize` parameter is an optional tuple that specifies the size of the figure for the bar chart visualization. It should be in the format `(width, height)`, where `width` and `height` are in inches. If not provided, a default size of (8, 6) will be used.
    return_type : str 
        What to return. This must be one of the following strings:
        - "plot"
        - "table"
                    
    Returns
    -------
    Output is returned depending on the value passed to the return_type argument:
    - "plot": Matplotlib or Seaborn plot object
    - "table": Pandas DataFrame

    Raises
    ------
    ValueError: If hrvar is not a string.

    Example
    -------
    >>> create_inc_bar(data = pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation", threshold = 20, position = "below", return_type = "plot")
    """

    # Transform data so that metrics become proportions
    data_t = data.copy()
    if position == "above":
        data_t[metric] = data_t[metric] >= threshold
    elif position == "below":
        data_t[metric] = data_t[metric] <= threshold
    else:
        raise ValueError("Please enter a valid input for `position`.")
    
    
    title_text = f"Incidence of {metric} {position} {threshold}" # Set title text    
    subtitle_text = f"Percentage and number of employees by {hrvar}" # Set subtitle text
    
    if return_type == 'data':
        return data_t
    else:    
        return create_bar(
            data_t,
            metric,
            hrvar,
            mingroup,
            percent = True,
            plot_title = title_text,
            plot_subtitle = subtitle_text,
            return_type = return_type,
            figsize=figsize
            )

def create_inc_grid(data: pd.DataFrame, metric: str, hrvar: typing.List, mingroup: int=5, threshold: float=None, position: str=None, return_type: str='plot', figsize: tuple = None):
    """
    Name
    -----
    create_inc_grid

    Description
    -----------
    Run `create_inc` with two `hrvar`.
    Returning a heatmap

    Parameters
    ----------
    data : pandas dataframe 
        A Standard Person Query dataset in the form of a Pandas DataFrame.
    metric : str
         Name of the metric, e.g. "Collaboration_hours".
    hrvar : list
         Names of the HR Variables by which to split metrics.
    mingroup : int
         Privacy threshold / minimum group size. Defaults to 5.
    threshold : float
         Threshold value to split the data based on the position argument. Defaults to None.
    position : str 
        One of the below valid values:
        - "above": show incidence of those equal to or above the threshold
        - "below": show incidence of those equal to or below the threshold
    figsize : tuple, optional
        The `figsize` parameter is an optional tuple that specifies the size of the figure for the heatmap visualization. It should be in the format `(width, height)`, where `width` and `height` are in inches. If not provided, a default size of (8, 6) will be used.
    return_type : str
        What to return. This must be one of the following strings:
        - "plot"
        - "table"
                    
    Returns
    -------
    Output is returned depending on the value passed to the return_type argument:
    - "plot": Matplotlib or Seaborn plot object
    - "table": Pandas DataFrame

    Raises
    ------
    ValueError: If hrvar is not a list of length 2.
    """

    if not isinstance(hrvar, list) or len(hrvar) != 2:
        raise ValueError("`hrvar` must be a list of length 2.")

    metric_to_pass = np.where(data[metric] >= threshold, 1, 0) \
        if position == "above" else np.where(data[metric] <= threshold, 1, 0) \
            if position == "below" else {}
    
    myTable: pd.DataFrame = (
        data
        .assign(metric_inc=metric_to_pass)
        .groupby(hrvar + ['PersonId'], as_index=False)
        .agg({'metric_inc': 'mean'})
        .groupby(hrvar, as_index=False)
        .agg({'metric_inc': 'mean', 'PersonId': 'nunique'})
        .rename(columns={'metric_inc': 'incidence', 'PersonId': 'count'})
        .query('count >= @mingroup')
        .sort_values('incidence', ascending=False)
        )

    if return_type == "table":
        
        return myTable

    elif return_type == "plot":

        # Set title text
        title_text = f"Incidence of {metric.replace('_', ' ').capitalize()} {position} {threshold}"

        # Set subtitle text
        subtitle_text = f"Percentage and number of employees by {hrvar[0]} and {hrvar[1]}"
        cap_str = extract_date_range(data, return_type = 'text')
        
        # Create the heatmap with the new annot DataFrame
        myTable['metric_text'] = myTable.apply(lambda row: f"{row['incidence']*100:.1f}% ({row['count']})", axis=1)
        
        # Order the columns and rows by the longest first to fit landscape plot
        if myTable[hrvar[0]].nunique() > myTable[hrvar[1]].nunique():
            hrvar = [hrvar[1], hrvar[0]]
            
        # Annotation to pass to heatmap    
        annot_df = myTable.pivot(index=hrvar[0], columns=hrvar[1], values='metric_text')
        
        # Setup plot size.
        fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))
        
        # Create grid 
        # Zorder tells it which layer to put it on. We are setting this to 1 and our data to 2 so the grid is behind the data.
        # ax.grid(which="major", axis='both', color='#758D99', alpha=0.6, zorder=1)        
        ax.grid(False)
        
        # Remove tick marks
        ax.tick_params(
            which='both',      # Both major and minor ticks are affected
            top=False,         # Remove ticks from the top
            bottom=False,      # Remove ticks from the bottom
            left=False,        # Remove ticks from the left
            right=False        # Remove ticks from the right
        )
        
        sns.set_theme(font_scale=0.7)
        # plot heatmap
        sns.heatmap(
            myTable.pivot(index=hrvar[0], columns=hrvar[1], values='incidence'),
            annot = annot_df,
            fmt='',
            cmap=COLOR_PALLET_ALT_2,
            center=0.5,
            square=True,
            ax=ax
            )

        # Add in line and tag
        ax.plot(
            [0, .9], # Set width of line, previously [-0.08, .9]
            [0.9, 0.9], # Set height of line
            # [1.17, 1.17], # Set height of line
            transform = fig.transFigure, # Set location relative to plot
            clip_on = False,
            color = '#fe7f4f',
            linewidth = .6
        )

        ax.add_patch(
            plt.Rectangle(
                (0, 0.9), # Set location of rectangle by lower left corner, previously [-0.08, .9]
                0.05, # Width of rectangle
                -0.025, # Height of rectangle
                facecolor = '#fe7f4f',
                transform = fig.transFigure,
                clip_on = False,
                linewidth = 0
                )
        )        
        
        # Set title
        ax.text(
            x = 0, y = 1.00,
            s = title_text,
            transform = fig.transFigure,
            ha = 'left',
            fontsize = 13,
            weight = 'bold',
            alpha = .8
        )
        
        # Set subtitle
        ax.text(
            x = 0, y = 0.95,
            s = subtitle_text,
            transform = fig.transFigure,
            ha = 'left',
            fontsize = 11,        
            alpha = .8
        )
        
        # Set caption
        ax.text(x=0, y=0.02, s=cap_str, transform=fig.transFigure, ha='left', fontsize=9, alpha=.7)  
        
        # return the plot object
        return fig
        # plt.show()
           
        """ Legacy
        ax.set(title=title_text, xlabel=hrvar[1], ylabel=hrvar[0], aspect='equal')
        ax.text(1.1, 1.05, subtitle_text, transform=ax.transAxes, fontsize=14, va='center')        
        """
    else: 
        raise ValueError("Please enter a valid input for `return_type`: Either `table` or `plot`.")