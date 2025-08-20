# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from vivainsights.create_boxplot import create_boxplot

def identify_habit(
    data,
    metric,
    threshold=1,
    width=1,
    max_window=4,  # Set a default value for max_window
    hrvar=None,
    return_type="plot",
    plot_mode="time",
    figsize: tuple = None,
    fill_col=("#E5E5E5", "#0078D4")):
    """
    Name
    -----
    identify_habit

    Description
    -----------
    Identify habitual behavior over a given interval of time. This function analyzes 
    a dataset to determine whether a habit exists based on a specified metric and 
    thresholds. It can return data, plots, or summary statistics depending on the 
    `return_type` argument.

    Parameters
    ----------
    data : pandas.DataFrame
        A dataset containing the data to analyze. Must include 'PersonId', 'MetricDate', 
        and the metric column.
    metric : str
        Column name of the metric to analyze.
    threshold : int, optional
        Minimum value for a week to be considered a qualifying count. Default is 1.
    width : int, optional
        Number of qualifying counts required for a habit.
    max_window : int, optional
        Maximum number of periods to consider for a habit.
    hrvar : str, optional
        Column name for grouping (e.g., department or team). Default is None.
    return_type : str, optional
        Type of output to return. Must be one of the following:
        - "data": Returns a DataFrame with habit classification.
        - "plot": Returns a plot of habitual behavior.
        - "summary": Returns summary statistics.
        Default is "plot".
    plot_mode : str, optional
        Type of plot to generate if `return_type` is "plot". Must be one of the following:
        - "time": Time series plot of habitual behavior.
        - "boxplot": Boxplot of habitual behavior by group.
        Default is "time".
    figsize : tuple, optional
        The `figsize` parameter is an optional tuple that specifies the size of the figure for the boxplot visualization. It should be in the format `(width, height)`, where `width` and `height` are in inches. If not provided, a default size of (8, 6) will be used.
    fill_col : tuple, optional
        Colors for the plot. Default is ("#E5E5E5", "#0078D4").

    Returns
    -------
    Depending on the value of `return_type`, the function returns:
    - pandas.DataFrame: If `return_type` is "data".
    - matplotlib plot: If `return_type` is "plot".
    - dict: Summary statistics if `return_type` is "summary".

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.identify_habit(pq_data, metric='Multitasking_hours', threshold=1, width=9, max_window=12, return_type="data")
    >>> vi.identify_habit(pq_data, metric='Multitasking_hours', threshold=1, width=9, max_window=12, return_type="plot", plot_mode="time")
    >>> vi.identify_habit(pq_data, metric='Multitasking_hours', threshold=1, width=9, max_window=12, return_type="summary")
    """
    # Ensure MetricDate is a datetime object
    data['MetricDate'] = pd.to_datetime(data['MetricDate'])
    
    # Validate max_window
    if not isinstance(max_window, int) or max_window <= 0:
        raise ValueError("`max_window` must be a positive integer.")

    # Validate width
    if not isinstance(width, int) or width <= 0:
        raise ValueError("`width` must be a positive integer.")

    # Calculate cumulative sums and habit classification
    data = data.sort_values(by=['PersonId', 'MetricDate'])
    data['cumsum_value'] = data.groupby('PersonId')[metric].transform(lambda x: (x >= threshold).cumsum())
    data['lagged_cumsum'] = data.groupby('PersonId')['cumsum_value'].shift(max_window, fill_value=0)
    data['sum_last_w'] = data['cumsum_value'] - data['lagged_cumsum']
    data['IsHabit'] = data['sum_last_w'] >= width

    if return_type == "data":
        return data

    elif return_type == "plot":
        if plot_mode == "time":
            # Time series plot
            habit_summary = (
                data.groupby(['MetricDate', 'IsHabit'])
                .agg(n=('PersonId', 'nunique'))
                .reset_index()
            )
            habit_summary['IsHabit'] = habit_summary['IsHabit'].map({True: "Habit", False: "No Habit"})
            habit_pivot = habit_summary.pivot(index='MetricDate', columns='IsHabit', values='n').fillna(0)
            habit_pivot = habit_pivot.div(habit_pivot.sum(axis=1), axis=0)  # Convert to percentages

            # Plot with improved formatting
            fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))
            habit_pivot.plot(
                kind='bar',
                stacked=True,
                color=fill_col[::-1],  # Reverse colors to stack blue below grey
                ax=ax
            )
            ax.set_title(f"Habitual Behavior - {metric.replace('_', ' ')}", fontsize=14, fontweight="bold")
            ax.set_ylabel("Percentage", fontsize=12)
            ax.set_xlabel("MetricDate", fontsize=12)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{int(y * 100)}%"))  # Format y-axis as percentages
            ax.legend(title="Is Habit", labels=["No Habit", "Habit"], fontsize=10)
            ax.set_xticks(range(len(habit_pivot.index)))
            ax.set_xticklabels(habit_pivot.index.strftime("%b %d, %y"), rotation=45, ha="right")  # Format x-axis dates
            plt.tight_layout()
            return fig  # Return the figure object

        elif plot_mode == "boxplot":
            # Use create_boxplot for boxplot
            plot_data = data.copy()
            
            # Convert 'IsHabit' to numeric for boxplot
            plot_data['IsHabit'] = plot_data['IsHabit'].astype(int)           
            
            return create_boxplot(data=plot_data, metric='IsHabit', hrvar=hrvar, mingroup=1, return_type="plot")

        else:
            raise ValueError("Invalid plot mode")

    elif return_type == "summary":
        # Summary statistics
        recent_stats = data[data['MetricDate'] == data['MetricDate'].max()]
        recent_summary = {
            "Most recent week - Total persons with habit": recent_stats['IsHabit'].sum(),
            "Most recent week - % of pop with habit": recent_stats['IsHabit'].mean(),
        }

        dist_summary = {
            "Mean - % of Person-weeks with habit": data['IsHabit'].mean(),
            "Median - % of Person-weeks with habit": data['IsHabit'].median(),
            "Min - % of Person-weeks with habit": data['IsHabit'].min(),
            "Max - % of Person-weeks with habit": data['IsHabit'].max(),
            "SD - % of Person-weeks with habit": data['IsHabit'].std(),
        }

        person_week_summary = {
            "Total Person-weeks with habit": data['IsHabit'].sum(),
            "Total Person-weeks": len(data),
            "% of Person-weeks with habit": data['IsHabit'].mean(),
            "Total Persons": data['PersonId'].nunique(),
            "Total Weeks": data['MetricDate'].nunique(),
        }

        return {**recent_summary, **dist_summary, **person_week_summary}

    else:
        raise ValueError("Invalid return type")