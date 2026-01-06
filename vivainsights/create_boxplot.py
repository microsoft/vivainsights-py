# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
The function `create_boxplot` creates a boxplot visualization and summary table for a given metric
and grouping variable in a dataset.
"""

__all__ = ['create_boxplot_calc', 'create_boxplot_summary', 'create_boxplot_viz', 'create_boxplot']

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from vivainsights.extract_date_range import extract_date_range
from vivainsights.color_codes import *
from vivainsights.totals_col import *

def create_boxplot_calc(data: pd.DataFrame, metric, hrvar, mingroup):
        # Data calculations    
        plot_data = (
        data.rename(columns={hrvar: "group"}) # Rename hrvar to "group"
            .groupby(["PersonId", "group"], as_index=False)[metric]
            .mean()
            .merge(
                data.rename(columns={hrvar: "group"}) # Rename hrvar to "group"
                    .groupby("group", as_index=False)["PersonId"]
                    .nunique()
                    .rename(columns={"PersonId": "Employee_Count"}),
                on="group"
            )
            .query("Employee_Count >= @mingroup")
            )
        # Data legend calculations    
        plot_legend = (
            plot_data.groupby("group", as_index=False)
                .first()
                .merge(
                    plot_data.groupby("group", as_index=False)["Employee_Count"]
                        .first()
                        .rename(columns={"Employee_Count": "n"}),
                    on="group"
                )
                .assign(Employee_Count=lambda x: x["n"].astype(str))
                .loc[:, ["group", "Employee_Count"]]
                )
        return(plot_data)


def create_boxplot_summary(data: pd.DataFrame, metric, hrvar, mingroup):

        # Data calculations            
        plot_data = create_boxplot_calc(data, metric, hrvar, mingroup)
        
        # Summary table
        summary_table = (
            plot_data.groupby("group", as_index=False)[metric]
            .agg(["mean", "median", "std", "min", "max", "count"])
            .rename(columns={"mean": "mean", "median": "median", "std": "sd", "min": "min", "max": "max", "count": "n"})
        )
        return(summary_table)


def create_boxplot_viz(data: pd.DataFrame, metric, hrvar, mingroup,figsize: tuple = None):    
        
        # Clean labels for plotting
        clean_nm = metric.replace("_", " ")
        cap_str = extract_date_range(data, return_type = 'text')
        
        # Calculate 'plot data'
        data = create_boxplot_calc(data, metric, hrvar, mingroup)
        
        # Get max value
        max_point = data[metric].max() * 1.2
        
        # Boxplot Vizualization
        col_highlight = Colors.HIGHLIGHT_NEGATIVE.value
        col_main = Colors.PRIMARY.value
        
        # Setup plot size.
        fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))
        
        # Create grid 
        # Zorder tells it which layer to put it on. We are setting this to 1 and our data to 2 so the grid is behind the data.
        # ax.grid(which="major", axis='both', color='#758D99', alpha=0.6, zorder=1)
        ax.grid(False)
        
        # Remove splines. Can be done one at a time or can slice with a list.
        ax.spines[['top','right','left']].set_visible(False)
        
        # Generate boxplot
        sns.boxplot(x='group', y=metric, data= data, ax=ax)
        
        # Add in line and tag
        ax.plot(
            [0, .9], # Set width of line, previously [-0.08, .9]
            [0.9, 0.9], # Set height of line
            # [1.17, 1.17], # Set height of line
            transform = fig.transFigure, # Set location relative to plot
            clip_on = False,
            color = col_highlight,
            linewidth = .6
        )
        ax.add_patch(
            plt.Rectangle(
                (0, 0.9), # Set location of rectangle by lower left corner, previously [-0.08, .9]
                0.05, # Width of rectangle
                -0.025, # Height of rectangle
                facecolor = col_highlight,
                transform = fig.transFigure,
                clip_on = False,
                linewidth = 0
                )
        )
        
        # Set title
        ax.text(
            x = 0, y = 1.00,
            s = (f"Distribution of {clean_nm.lower()}"),
            transform = fig.transFigure,
            ha = 'left',
            fontsize = 13,
            weight = 'bold',
            alpha = .8
        )
        
        # Set subtitle
        ax.text(
            x = 0, y = 0.95,
            s = f'By {hrvar}',
            transform = fig.transFigure,
            ha = 'left',
            fontsize = 11,        
            alpha = .8
        )
        
        # Set caption
        ax.text(x=0, y=-0.08, s=cap_str, transform=fig.transFigure, ha='left', fontsize=9, alpha=.7)

        # plt.show()
        # return the plot object
        return fig    
    
        """ ggplot implementation - legacy
        plot_object = (
        ggplot(plot_data, aes(x="group", y=metric)) +
        geom_boxplot(color="#578DB8",varwidth=True) +
        ylim(0, max_point) +
        theme(figure_size=(16,8),
              axis_text=element_text(size=12),
              axis_text_x=element_text(angle=0, hjust=1,size=12, linespacing=10,ha='center',va='center'),
              plot_title=element_text(color="grey", face="bold", size=18),
              legend_position="bottom",
              legend_title=element_text(size=14),
              legend_text=element_text(size=14)) +
        labs(title=clean_nm + (f"\n\nDistribution of {clean_nm.lower()} by {hrvar.lower().replace('_', ' ')}"),
             x=hrvar,
             y=f"Average {clean_nm}",
             caption=(extract_date_range(data, return_type="text"))
             ))
        return(plot_object)
        """
    
def create_boxplot(data: pd.DataFrame, metric: str, hrvar: str ="Organization", mingroup=5, return_type: str = "plot", figsize: tuple = None):
    """
    Name
    -----
    create_boxplot

    Description
    -----------
    This function creates a boxplot visualization and summary table for a given metric and HR variable
    in a pandas DataFrame.
    
    Parameters
    ----------
    data : pandas dataframe
        A pandas DataFrame containing the data for analysis.
    metric : str
        The `metric` parameter is a string that represents the variable or metric for which you want to create the boxplot visualization and summary table. This variable should be present in the input data` DataFrame.
    hrvar : str, optional
        The `hrvar` parameter is the HR variable that you want to use for grouping the data. By default, it is set to "Organization", but you can pass a different HR variable if needed.
    mingroup: int, optional
        The `mingroup` parameter is an optional parameter that specifies the minimum number of observations required in each group for the boxplot to be created. If a group has fewer observations than the `mingroup` value, it will be excluded from the boxplot. The default value is 5.
    figsize : tuple, optional
        The `figsize` parameter is an optional tuple that specifies the size of the figure for the boxplot visualization. It should be in the format `(width, height)`, where `width` and `height` are in inches. If not provided, a default size of (8, 6) will be used.
    return_type : str, optional
        The `return_type` parameter determines the type of output that the function will return. It can take one of three values:
    
    Returns
    -------
    The function `create_boxplot` returns different outputs based on the value of the `return_type` parameter

    Example
    -------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.create_boxplot(pq_data, metric = "Collaboration_hours", hrvar = "Organization", return_type = "plot")
    
    """
    # Check inputs
    required_variables = ["MetricDate", metric, "PersonId"]

    # Error message if variables are not present and Nothing happens if all present
    assert all(var in data.columns for var in required_variables), f"Missing required variable(s): {set(required_variables) - set(data.columns)}"

    # Handling NULL values passed to hrvar
    if hrvar is None:
        data = totals_col(data)
        hrvar = "Total"          
    
    # Main output
    if return_type == "table":  
        # Data calculations
        plot_data = create_boxplot_calc(data, metric, hrvar, mingroup)      
        
        # Summary table
        summary_table = create_boxplot_summary(plot_data, metric, hrvar, mingroup)
        
        return pd.DataFrame(summary_table).reset_index()
    
    elif return_type == "plot":
        # Boxplot vizualization    
        plot_object = create_boxplot_viz(data, metric, hrvar, mingroup,figsize)
        return plot_object
    elif return_type == "data":
        # Data calculations
        plot_data = create_boxplot_calc(data, metric, hrvar, mingroup)
        
        # Summary table
        summary_table = create_boxplot_summary(plot_data, metric, hrvar, mingroup)
        
        # Group order
        group_ord = summary_table.sort_values(by="mean", ascending=True)["group"].tolist()
    
        # Create a new column in plot_data with the same name as the group variable
        plot_data = plot_data.assign(group=pd.Categorical(plot_data.group, categories=group_ord)).sort_values(by="group", ascending=False)
        
        return plot_data
    else:
        raise ValueError("Please enter a valid input for `return`.")
