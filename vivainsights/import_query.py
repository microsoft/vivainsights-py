# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Import a Viva Insights query from a CSV file with optimized variable types.

The function takes in a file path (x)
and an optional encoding parameter (default is 'utf-8'). It checks if the file is a .csv file, reads
in the file using pandas, cleans the column names by removing spaces and special characters, and
returns the resulting data as a pandas dataframe. If there is an error reading the file, the function prints an error message.
"""

__all__ = ['import_query']

import pandas as pd
import re 
import os

def import_query(x, encoding: str = 'utf-8'):
    """
    Import a Viva Insights query from a CSV file.

    Reads the file, strips whitespace from column names and replaces spaces
    and special characters with underscores.

    Parameters
    ----------
    x : str
        Path to a ``.csv`` file.
    encoding : str, optional
        Character encoding for reading the file. Defaults to ``"utf-8"``.

    Returns
    -------
    pandas.DataFrame
        The imported data with cleaned column names.

    Raises
    ------
    ValueError
        If the file does not exist, is not a CSV, or cannot be read.

    Examples
    --------
    >>> import vivainsights as vi
    >>> data = vi.import_query("path/to/query.csv")
    """    
    
    # in case '.csv' is not all in lower case, make it lower case
    if x[-4:].lower() == '.csv':
        in_df = x[:-4] + '.csv'
    else:
        in_df = x
        
    if not os.path.isfile(in_df):
        raise ValueError("input file does not exist")
    
    elif not in_df.endswith('.csv'):
        raise ValueError("the input must be a .csv file")
    
    else:
        try:
            # Try to read in csv file, if file can not be read, exception is thrown.
            data = pd.read_csv(x, encoding=encoding, delimiter=',')
            # Replace mentions of '%' with literal string 'Percent'
            data.columns = [re.sub('%', 'Percent', c.strip()) for c in data]
            # Remove leading and trailing spaces
            # Remove spaces and special characters and replacing them with underscores within column names.
            data.columns = [re.sub('[^a-zA-Z0-9,]', '_', c.strip()) for c in data]
            
            return data
        except: 
            raise ValueError('something went wrong when reading the file')
