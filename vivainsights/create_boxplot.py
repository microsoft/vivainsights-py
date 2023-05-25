# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
The function `create_boxplot` creates a boxplot visualization and summary table for a given metric
and grouping variable in a dataset.

:param data: The input data for the boxplot, which should be a pandas DataFrame
:param total_value: `total_value` is a parameter in the `totals_col` function that specifies the
name of the new column to be added to the input data with a constant value of "Total", defaults to
Total (optional)
:return: The `create_boxplot()` function returns either a summary table, a plot object, or a data
frame depending on the value of the `return_type` parameter.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from vivainsights.extract_date_range import extract_date_range
from vivainsights.color_codes import *

def totals_col(data: pd.DataFrame, total_value='Total'):
    if total_value in data.columns:
        raise ValueError(f"Column '{total_value}' already exists. Please supply a different value to `total_value`")

    data[total_value] = total_value
    return data

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


def create_boxplot_viz(data: pd.DataFrame, metric, hrvar, mingroup):    
        
        # Get max value
        max_point = data[metric].max() * 1.2
        
        # Clean labels for plotting
        clean_nm = metric.replace("_", " ")
        cap_str = extract_date_range(data, return_type = 'text')
        
        # Boxplot Vizualization
        col_highlight = Colors.HIGHLIGHT_NEGATIVE.value
        col_main = Colors.PRIMARY.value
        
        # Setup plot size.
        fig, ax = plt.subplots(figsize=(7,4))
        
        # Create grid 
        # Zorder tells it which layer to put it on. We are setting this to 1 and our data to 2 so the grid is behind the data.
        # ax.grid(which="major", axis='both', color='#758D99', alpha=0.6, zorder=1)
        ax.grid(False)
        
        # Remove splines. Can be done one at a time or can slice with a list.
        ax.spines[['top','right','left']].set_visible(False)
        
        # Generate boxplot
        sns.boxplot(x='Organization', y='Emails_sent', data= data, ax=ax)
        
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

        plt.show()          
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
    
def create_boxplot(data: pd.DataFrame, metric: str, hrvar: str ="Organization", mingroup=5, return_type: str = "plot"):
    """
    This function creates a boxplot visualization and summary table for a given metric and HR variable
    in a pandas DataFrame.
    
    :param data: A pandas DataFrame containing the data to be used for creating the boxplot
    :type data: pd.DataFrame
    :param metric: The metric variable is a string representing the name of the metric being analyzed in
    the boxplot
    :type metric: str
    :param hrvar: `hrvar` stands for the variable that represents the grouping variable for the boxplot.
    By default, it is set to "Organization", but it can be changed to any other variable in the input
    data. If `hrvar` is set to None, the function will calculate the boxplot for, defaults to
    Organization
    :type hrvar: str (optional)
    :param mingroup: `mingroup` is a parameter that specifies the minimum number of individuals required
    in each group for the boxplot to be created. If a group has fewer individuals than `mingroup`, it
    will not be included in the boxplot, defaults to 5 (optional)
    :param return_type: The parameter `return_type` specifies the type of output that the function
    should return. It can be set to "plot" to return a boxplot visualization, "table" to return a
    summary table, or "data" to return the calculated data used to create the boxplot. If an invalid,
    defaults to plot
    :type return_type: str (optional)
    :return: either a summary table, a plot object, or a plot data depending on the value of the
    `return_type` parameter.
    """

    # Check inputs
    required_variables = ["MetricDate", metric, "PersonId"]

    # Error message if variables are not present and Nothing happens if all present
    assert all(var in data.columns for var in required_variables), f"Missing required variable(s): {set(required_variables) - set(data.columns)}"

    # Handling NULL values passed to hrvar
    if hrvar is None:
        data = totals_col(data)
        hrvar = "Total"    

    # Summary table
    summary_table = create_boxplot_summary(data, metric, hrvar, mingroup)
        
    # Group order
    group_ord = summary_table.sort_values(by="mean", ascending=True)["group"].tolist()
    
    # Main output
    if return_type == "table":        
        return pd.DataFrame(summary_table).reset_index()
    elif return_type == "plot":
        # Boxplot vizualization    
        plot_object = create_boxplot_viz(data, metric, hrvar, mingroup)
        return plot_object
    elif return_type == "data":
        # Data calculations
        plot_data = create_boxplot_calc(data, metric, hrvar, mingroup)
        return plot_data.assign(group=pd.Categorical(plot_data.group, categories=group_ord)).sort_values(by="group", ascending=False)
    else:
        raise ValueError("Please enter a valid input for `return`.")
