# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
The function `extract_date_range` extracts the date range from a dataframe and returns it either as
a table or as a text string.

:param data: The `data` parameter is a pandas DataFrame that contains the data from which you want
to extract the date range. It should have at least one column that represents the date
:type data: pd.DataFrame
:param return_type: The `return_type` parameter is a string that specifies the format in which the
date range should be returned. It has two possible values:, defaults to table
:type return_type: str (optional)
:return: The function `extract_date_range` returns either a pandas DataFrame or a string, depending
on the value of the `return_type` parameter.
"""
import pandas as pd

def extract_date_range(data: pd.DataFrame, return_type: str = "table"):
    """Extracts the date range from a dataframe."""
    date_var = None
    
    if "Date" in data.columns:
        date_var = pd.to_datetime(data["Date"], format="%m/%d/%Y")
    elif "MetricDate" in data.columns:
        date_var = pd.to_datetime(data["MetricDate"], format="%Y-%m-%d")
    elif all(x in data.columns for x in ["StartDate", "EndDate"]):
        date_var = pd.to_datetime(data[["StartDate", "EndDate"]].stack().reset_index(drop=True), format="%m/%d/%Y")

    if date_var is None:
        raise ValueError("Error: no date variable found.")
    """
    Data frame to output
    """
    outTable = pd.DataFrame({"Start": date_var.min(), "End": date_var.max()}, index=[0])

    if return_type == "table":
        return outTable
    elif return_type == "text":
        return f"Data from {outTable.iloc[0]['Start'].strftime('%Y-%m-%d')} to {outTable.iloc[0]['End'].strftime('%Y-%m-%d')}"