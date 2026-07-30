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


def _clean_column_name(column_name):
    column_name = re.sub('%', 'Percent', column_name.strip())
    return re.sub('[^a-zA-Z0-9,]', '_', column_name)


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
    Import a standard Viva Insights CSV export:

    >>> import vivainsights as vi
    >>> data = vi.import_query("path/to/query.csv")

    Specify a custom encoding for non-UTF-8 files:

    >>> data = vi.import_query("path/to/query.csv", encoding="latin-1")
    """
    input_path = os.fspath(x)

    if not os.path.isfile(input_path):
        raise ValueError("input file does not exist")

    if not input_path.lower().endswith('.csv'):
        raise ValueError("the input must be a .csv file")

    try:
        data = pd.read_csv(input_path, encoding=encoding, delimiter=',')
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        raise ValueError(f"could not read CSV file: {exc}") from exc

    data.columns = [_clean_column_name(column) for column in data.columns]

    return data
