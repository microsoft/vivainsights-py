# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Identify outlier weeks using z-scores for a selected metric.

There are applications in this for identifying weeks with abnormally low collaboration activity, e.g. holidays. Time as a grouping variable can be overridden with the `group_var` argument.
"""

__all__ = ['identify_outlier']

import pandas as pd
    
def identify_outlier(data: pd.DataFrame, group_var = "MetricDate", metric = "Collaboration_hours"):
    
    """Identify outlier weeks using z-scores for a metric.

    Computes the mean of the metric per group (default: ``MetricDate``)
    and the corresponding z-scores to flag outliers.  Useful for
    detecting weeks with abnormally low collaboration, e.g. holidays.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.
    group_var : str, default "MetricDate"
        Grouping variable.
    metric : str, default "Collaboration_hours"
        Name of the metric column.

    Returns
    -------
    pandas.DataFrame
        A DataFrame indexed by *group_var* with the metric mean and a
        ``zscore`` column.

    Examples
    --------
    Detect outlier groups using the default grouping variable:

    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.identify_outlier(pq_data, metric="Collaboration_hours")

    Specify a custom grouping variable:

    >>> vi.identify_outlier(pq_data, metric="Collaboration_hours", group_var="LevelDesignation")
    """ 

    try:
        # Group by the grouping variable and calculate the mean of the metric
        main_table = data.groupby(group_var).agg({metric: "mean"})

        # Calculate the z-score of the metric
        main_table["zscore"] = (main_table[metric] - main_table[metric].mean()) / main_table[metric].std()
        return main_table
    except:
        # Check for the error in the input data

        requirements = [group_var, "PersonId", metric]

        # Check if the required variables are present
        for i in requirements:
            if i not in data.columns:
                raise ValueError("The required variable {} is not present in the dataframe.".format(i))
        
        # Check to see if the metric column is numeric
        if not pd.api.types.is_numeric_dtype(data[requirements[2]]):
            raise ValueError("The metric column {} is not numeric.".format(requirements[2]))