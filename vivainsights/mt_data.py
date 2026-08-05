# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Load a sample meeting query dataset.
"""

__all__ = ['load_mt_data']

try:
    from importlib import resources
    resources.files
except (ImportError, AttributeError):
    import importlib_resources as resources
import pandas as pd

def load_mt_data():
    """Load a sample meeting query dataset.

    Returns a DataFrame containing a de-identified sample of Viva Insights
    meeting query data.

    Returns
    -------
    pandas.DataFrame
        A meeting query dataset with one row per meeting.

    Examples
    --------
    >>> import vivainsights as vi
    >>> mt_data = vi.load_mt_data()
    """
    try:
        # Python 3.9+ with importlib.resources.files
        files = resources.files(__package__).joinpath('data', 'mt_data.csv')
        with resources.as_file(files) as csv_path:
            out = pd.read_csv(csv_path, encoding='utf-8')
    except (TypeError, FileNotFoundError):
        # Fallback for older Python or different package structure
        try:
            files = resources.files(__package__.rsplit('.', 1)[0]).joinpath('data', 'mt_data.csv')
            with resources.as_file(files) as csv_path:
                out = pd.read_csv(csv_path, encoding='utf-8')
        except Exception:
            print('Error: please report issue to repo maintainer')
            return None
    
    return out