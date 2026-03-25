# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Create boxplot visualizations of metric distributions by organizational group.

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
        """Compute person-level metric averages per HR group.

        Used internally by ``create_boxplot``.

        Parameters
        ----------
        data : pandas.DataFrame
            Person query data.
        metric : str
            Name of the metric column.
        hrvar : str
            Name of the organizational attribute for grouping.
        mingroup : int
            Minimum group size; groups below this threshold are dropped.

        Returns
        -------
        pandas.DataFrame
            Person-level averages with groups meeting the *mingroup*
            threshold.
        """
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
        """Return summary statistics for a metric by HR group.

        Parameters
        ----------
        data : pandas.DataFrame
            Person query data.
        metric : str
            Name of the metric column.
        hrvar : str
            Name of the organizational attribute for grouping.
        mingroup : int
            Minimum group size.

        Returns
        -------
        pandas.DataFrame
            Summary table with mean, median, standard deviation, min, max,
            and count per group.
        """

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
        """Create a boxplot visualization of metric distributions by group.

        Used internally by ``create_boxplot`` when ``return_type="plot"``.

        Parameters
        ----------
        data : pandas.DataFrame
            Person query data.
        metric : str
            Name of the metric column.
        hrvar : str
            Name of the organizational attribute for grouping.
        mingroup : int
            Minimum group size.
        figsize : tuple or None, default None
            Figure size ``(width, height)`` in inches.

        Returns
        -------
        matplotlib.figure.Figure
            The boxplot figure.
        """
        
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
    """Create a boxplot of metric distributions by organizational group.

    Generates a boxplot showing the distribution of a selected metric across
    groups defined by an HR variable.  Metrics are aggregated at the person
    level before plotting.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.
    metric : str
        Name of the metric to visualize.
    hrvar : str, default "Organization"
        Name of the organizational attribute for grouping.
    mingroup : int, default 5
        Minimum group size; smaller groups are excluded.
    return_type : str, default "plot"
        ``"plot"`` for a matplotlib figure, ``"table"`` for summary
        statistics, or ``"data"`` for the processed plot data.
    figsize : tuple or None, default None
        Figure size ``(width, height)`` in inches.  Defaults to ``(8, 6)``.

    Returns
    -------
    matplotlib.figure.Figure or pandas.DataFrame
        A boxplot figure, a summary table, or the processed data,
        depending on *return_type*.

    Examples
    --------
    Return a boxplot (default):

    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.create_boxplot(pq_data, metric="Collaboration_hours", hrvar="Organization")

    Return a summary table with mean, median, sd, min, max:

    >>> vi.create_boxplot(pq_data, metric="Collaboration_hours", hrvar="Organization", return_type="table")

    Return the processed person-level data:

    >>> vi.create_boxplot(pq_data, metric="Collaboration_hours", hrvar="Organization", return_type="data")

    Customize the figure size:

    >>> vi.create_boxplot(
    ...     pq_data,
    ...     metric="Collaboration_hours",
    ...     hrvar="LevelDesignation",
    ...     figsize=(12, 8),
    ... )
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
