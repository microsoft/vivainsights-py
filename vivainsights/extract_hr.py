# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Extract HR or organizational attribute columns from a Viva Insights dataset.

There is an option to return either just a list of the variable names
or a DataFrame containing only the variables themselves.
"""

__all__ = ['extract_hr']

import pandas as pd
def extract_hr(
    data: pd.DataFrame,
    max_unique: int = 50,
    exclude_constants: bool = True,
    return_type: str = "names"):
    """    
    Extract HR attributes (organizational data) by detecting variable class
    and number of unique values.

    Parameters
    ----------
    data : pandas.DataFrame
        Data from which to extract HR variables.
    max_unique : int
        Maximum number of unique values a column can have to be included.
        Defaults to 50.
    exclude_constants : bool
        Whether to exclude columns with only one unique value.
        Defaults to ``True``.
    return_type : str
        Output type. ``"names"`` (default) prints column names,
        ``"vars"`` returns the filtered DataFrame,
        ``"suggestion"`` returns a list of column names.

    Returns
    -------
    pandas.DataFrame, list of str, or None
        Depends on ``return_type``: a DataFrame of HR columns, a list of
        column names, or prints names to console.

    Examples
    --------
    Print HR variable names to console (default):

    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.extract_hr(data=pq_data)

    Return the HR columns as a filtered DataFrame:

    >>> vi.extract_hr(data=pq_data, return_type="vars")

    Return a list of suggested HR column names:

    >>> vi.extract_hr(data=pq_data, return_type="suggestion")

    Adjust the maximum unique values threshold:

    >>> vi.extract_hr(data=pq_data, max_unique=50, return_type="names")
    """
    try:
        if((isinstance(max_unique, int)) and (isinstance(exclude_constants, bool))\
        and (return_type.lower() == "names") or (return_type.lower() == "vars") or (return_type.lower() == "suggestion")):
            unqdf = data.loc[:,data.nunique()<=max_unique]

        if exclude_constants == False:
            unqdf = unqdf.loc[:,unqdf.nunique()!=1]
  
        elif not isinstance(max_unique, int):
            error ="Error! var max_unique should be an integer value. Please try again."

        elif not isinstance(exclude_constants, bool):
            error ="Error! var exclude_constants should be an boolean(True/False) value. Please try again."

        elif (return_type.lower() != "names") or (return_type.lower() != "vars") or (return_type.lower() != "suggestion"):
            error = "Please check input to `return_type`."

        if return_type == "vars":
            return unqdf.select_dtypes(['object'])
        
        if return_type == "suggestion":
            return unqdf.select_dtypes(['object']).columns.tolist()
        
        #return print(*unqdf.columns+',\n')
        return print(*unqdf.select_dtypes(['object']).columns+',\n')
    
    except:
        print(error)