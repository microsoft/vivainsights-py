# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
The function `identify_inactiveweeks` identifies weeks where collaboration hours are more than a
specified number of standard deviations below the mean and returns the result in the specified
format.
"""
import pandas as pd
from vivainsights.create_bar import create_bar_calc

def identify_inactiveweeks(data: pd.DataFrame, sd=2, return_type="text"):
    """
    Name
    ----
    identify_inactiveweeks

    Description
    -----------
    The function `identify_inactiveweeks` identifies weeks where collaboration hours are more than a
    specified number of standard deviations below the mean and returns the result in the specified
    format.
    
    Parameters
    ----------
    data : pandas dataframe
        The `data` parameter is a pandas DataFrame that contains the following columns:
    sd : int
        The `sd` parameter stands for the number of standard deviations below the mean that is considered as inactive. In this code, it is used to identify weeks where the collaboration hours are more than `sd` standard deviations below the mean, defaults to 2 (optional)
    return_type : str
         The `return_type` parameter determines the type of output that the function will return. It can have the following values:, defaults to text (optional)
    
    Returns
    -------
    The function `identify_inactiveweeks` returns different outputs based on the value of the `return_type` parameter.
    """
    # Z score calculation    
    data['z_score'] = (data['Collaboration_hours'] - data.groupby('PersonId')['Collaboration_hours'].transform('mean')) / data.groupby('PersonId')['Collaboration_hours'].transform('std')
    Calc = data[data["z_score"] <= -sd][["PersonId", "MetricDate", "z_score"]].reset_index(drop=True)

    # standard deviations below the mean
    data['Total'] = 'Total'
    result = create_bar_calc(data, metric='Collaboration_hours', hrvar='Total')
    collab_hours = result['metric'].round(1).to_frame()["metric"][0]

    # output when return_type is text
    message = f"There are {Calc.shape[0]} rows of data with weekly collaboration hours more than {sd} standard deviations below the mean {collab_hours}."
    
    # Output conditions based on return_type
    if return_type == "text":
        return message
    elif return_type == "data_dirty":
        return data[data["z_score"] <= -sd].drop(columns=["z_score"])
    elif return_type == "data_cleaned":
        return data[data["z_score"] > -sd].drop(columns=["z_score"])
    elif return_type == "data":
        return data.assign(inactiveweek=(data["z_score"] <= -sd)).drop(columns=["z_score"])
    else:
        raise ValueError("Error: please check inputs for `return_type`")
