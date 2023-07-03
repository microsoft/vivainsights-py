# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
The function `totals_col` adds a new column with a specified total value to a given pandas DataFrame.
"""
import pandas as pd

def totals_col(data: pd.DataFrame, total_value: str ='Total'):
    '''    
    Parameters
    ----------
    data : pd.DataFrame
        A pandas DataFrame that represents the data you want to add a totals column to.
    total_value, optional
        The `total_value` parameter is a string that represents the name of the new column that will be
    added to the DataFrame. By default, it is set to 'Total'.
    
    Returns
    -------
        The function `totals_col` returns the modified DataFrame `data` with a new column added.
    
    '''
    if total_value in data.columns:
        raise ValueError(f"Column '{total_value}' already exists. Please supply a different value to `total_value`")

    data[total_value] = total_value
    return data