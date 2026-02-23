# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Extract the minimum and maximum date range from a dataset.
"""
import pandas as pd

__all__ = ['extract_date_range']

def extract_date_range(data: pd.DataFrame, return_type: str = "table"):
    """
    Extract the date range from a DataFrame.

    Looks for ``Date``, ``MetricDate``, or ``StartDate``/``EndDate`` columns
    and returns the minimum and maximum dates.

    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame containing at least one recognised date column.
    return_type : str
        ``"table"`` (default) returns a single-row DataFrame with ``Start``
        and ``End`` columns; ``"text"`` returns a human-readable string.

    Returns
    -------
    pandas.DataFrame or str
        Date range as a table or descriptive string.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.extract_date_range(pq_data)
    >>> vi.extract_date_range(pq_data, return_type="text")
    """
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