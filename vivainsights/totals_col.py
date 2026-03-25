# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Add a totals column with a specified value to a DataFrame.
"""

__all__ = ['totals_col']

import pandas as pd

def totals_col(data: pd.DataFrame, total_value: str ='Total'):
    """
    Add a new column with a specified total value to a DataFrame.

    Parameters
    ----------
    data : pandas.DataFrame
        Input DataFrame.
    total_value : str, optional
        Name and fill value for the new column. Defaults to ``"Total"``.

    Returns
    -------
    pandas.DataFrame
        The input DataFrame with the new column appended.

    Raises
    ------
    ValueError
        If a column named ``total_value`` already exists.

    Examples
    --------
    Add a default "Total" column:

    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.totals_col(pq_data, total_value="Total")

    Use a custom label:

    >>> vi.totals_col(pq_data, total_value="AllEmployees")
    """
    if total_value in data.columns:
        raise ValueError(f"Column '{total_value}' already exists. Please supply a different value to `total_value`")

    data[total_value] = total_value
    return data