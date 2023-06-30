# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This function takes in a selected metric and uses the z-score (number of standard deviations) to identify outliers across time. There are applications in this for identifying weeks with abnormally low collaboration activity, e.g. holidays. Time as a grouping variable can be overridden with the `group_var` argument.
"""

import pandas as pd
    
def identify_outlier(data: pd.DataFrame, group_var = "MetricDate", metric = "Collaboration_hours"):
    
    """
    Name
    -----
    identify_outlier 
    
    Description
    -----------
    This function takes in a selected metric and uses the
    z-score (number of standard deviations) to identify outliers
    across time. There are applications in this for identifying
    weeks with abnormally low collaboration activity, e.g. holidays.
    Time as a grouping variable can be overridden with the `group_var`
    argument.

    Parameters
    ----------
    data : pandas dataframe
        A Standard Person Query dataset in the form of a pandas dataframe.
    group_var : str
        A string with the name of the grouping variable. Default: `MetricDate`.
    metric : str
        A string containing the name of the metric (e.g., "Collaboration_hours")

    Returns
    -------
    A dataframe with `MetricDate` (if grouping variable is not set),
    the metric, and the corresponding z-score. 

    Example
    -------
    >>> identify_outlier(data, group_var = "MetricDate", metric = "Collaboration_hours")
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