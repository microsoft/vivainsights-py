# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Count the number of distinct persons by organizational group.

Returns a bar plot of the counts by default, with an option to return a summary table.
"""

__all__ = ['hrvar_count_calc', 'hrvar_count_viz', 'hrvar_count_all', 'hrvar_count']

import pandas as pd
import matplotlib.pyplot as plt
from vivainsights.extract_date_range import extract_date_range
from vivainsights.extract_hr import extract_hr

def hrvar_count_calc(data: pd.DataFrame, hrvar: str):
    """Calculate the number of distinct persons in the data population, grouped by a selected HR variable.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.
    hrvar : str
        Name of the organizational attribute for grouping.

    Returns
    -------
    pandas.DataFrame
        Summary table with unique person count per group.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.hrvar_count_calc(pq_data, hrvar="Organization")
    """
    data = data.groupby([hrvar])
    data = data['PersonId'].nunique().reset_index(name='n')
    output = data.sort_values(by = 'n', ascending=False)
    return output

def hrvar_count_viz(data: pd.DataFrame, hrvar: str, figsize: tuple = None):
    """Visualise the number of distinct persons in the data population, grouped by a selected HR variable.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.
    hrvar : str
        Name of the organizational attribute for grouping.
    figsize : tuple or None, default None
        Figure size ``(width, height)`` in inches.

    Returns
    -------
    matplotlib.figure.Figure
        The bar chart figure.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.hrvar_count_viz(pq_data, hrvar="Organization")
    """
    sum_df = hrvar_count_calc(data = data, hrvar = hrvar)
    cap_str = extract_date_range(data, return_type = 'text')
    
    fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))
    
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

def hrvar_count_all(data: pd.DataFrame, hrvar_list: list = None, max_unique: int = 50):
    """
    Create a summary table to validate organizational data.

    Returns the count of distinct fields per HR attribute and the percentage
    of employees with missing values for that attribute.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.
    hrvar_list : list of str, optional
        HR variables to analyze. If ``None``, uses ``extract_hr()`` to
        dynamically identify organizational attributes.
    max_unique : int, optional
        Maximum number of unique values for a column to be considered an
        HR variable (only used when ``hrvar_list`` is ``None``).
        Defaults to 50.

    Returns
    -------
    pandas.DataFrame
        Summary table with columns ``hrvar``, ``distinct_values``,
        ``missing_count``, and ``missing_percentage``.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.hrvar_count_all(pq_data)
    >>>
    >>> vi.hrvar_count_all(pq_data, max_unique=100)
    """
    # Default HR variables if none provided - use extract_hr to dynamically detect
    if hrvar_list is None:
        available_hrvars = extract_hr(data, max_unique=max_unique, return_type="suggestion")
    else:
        # Filter to only include columns that exist in the data
        available_hrvars = [var for var in hrvar_list if var in data.columns]
    
    if not available_hrvars:
        raise ValueError("None of the specified HR variables exist in the data. Available columns: " + str(list(data.columns)))
    
    # Calculate summary statistics for each HR variable
    summary_data = []
    total_rows = len(data)
    
    for hrvar in available_hrvars:
        distinct_count = data[hrvar].nunique()
        missing_count = data[hrvar].isna().sum()
        missing_percentage = (missing_count / total_rows) * 100
        
        summary_data.append({
            'hrvar': hrvar,
            'distinct_values': distinct_count,
            'missing_count': missing_count,
            'missing_percentage': round(missing_percentage, 1)
        })
    
    # Create DataFrame and sort by missing percentage (descending) to highlight problematic variables first
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('missing_percentage', ascending=False).reset_index(drop=True)
    
    return summary_df

def hrvar_count(data: pd.DataFrame, hrvar: str = 'Organization', figsize: tuple = None, return_type: str = "plot"):
    """
    Count distinct persons in the data population grouped by an HR variable.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.
    hrvar : str
        Organizational attribute for grouping. Defaults to ``"Organization"``.
    figsize : tuple, optional
        Figure size as ``(width, height)`` in inches. Defaults to ``(8, 6)``.
    return_type : str
        ``"plot"`` (default) returns a bar chart; ``"table"`` returns a
        summary DataFrame.

    Returns
    -------
    matplotlib.figure.Figure or pandas.DataFrame
        Bar chart or summary table depending on ``return_type``.

    Examples
    --------
    Return a bar chart (default):

    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.hrvar_count(pq_data, hrvar="LevelDesignation")

    Return a summary table:

    >>> vi.hrvar_count(pq_data, hrvar="Organization", return_type="table")

    Customize figure size:

    >>> vi.hrvar_count(pq_data, hrvar="LevelDesignation", figsize=(10, 5))
    """
    if return_type == "plot":
        out = hrvar_count_viz(data=data, hrvar=hrvar, figsize=figsize)
    elif return_type == "table":
        out = hrvar_count_calc(data=data, hrvar=hrvar)
    else:
        out = "Invalid input. Please check your inputs and try again."
    return out