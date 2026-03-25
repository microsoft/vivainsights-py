# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Load a sample group-to-group query dataset.

Example
-------
>>> import vivainsights as vi
>>> g2g_data = vi.load_g2g_data()
"""

__all__ = ['load_g2g_data']

import importlib.resources
import pandas as pd

def load_g2g_data():
    """Load a sample group-to-group query dataset.

    Returns a DataFrame containing a de-identified sample of Viva Insights
    group-to-group query data.

    Returns
    -------
    pandas.DataFrame
        A group-to-group query dataset.

    Examples
    --------
    >>> import vivainsights as vi
    >>> g2g_data = vi.load_g2g_data()
    """
    try:
        # Python 3.9+ with importlib.resources.files
        files = importlib.resources.files(__package__).joinpath('data', 'g2g_data.csv')
        with importlib.resources.as_file(files) as csv_path:
            out = pd.read_csv(csv_path, encoding='utf-8')
    except (TypeError, FileNotFoundError):
        # Fallback for older Python or different package structure
        try:
            files = importlib.resources.files(__package__.rsplit('.', 1)[0]).joinpath('data', 'g2g_data.csv')
            with importlib.resources.as_file(files) as csv_path:
                out = pd.read_csv(csv_path, encoding='utf-8')
        except Exception:
            print('Error: please report issue to repo maintainer')
            return None
    
    return out