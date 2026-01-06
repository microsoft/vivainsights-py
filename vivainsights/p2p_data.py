# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module returns a data frame containing a person-to-person query.
"""

__all__ = ['load_p2p_data']

import importlib.resources
import pandas as pd

def load_p2p_data():
    try:
        # Python 3.9+ with importlib.resources.files
        files = importlib.resources.files(__package__).joinpath('data', 'p2p_data.csv')
        with importlib.resources.as_file(files) as csv_path:
            out = pd.read_csv(csv_path, encoding='utf-8')
    except (TypeError, FileNotFoundError):
        # Fallback for older Python or different package structure
        try:
            files = importlib.resources.files(__package__.rsplit('.', 1)[0]).joinpath('data', 'p2p_data.csv')
            with importlib.resources.as_file(files) as csv_path:
                out = pd.read_csv(csv_path, encoding='utf-8')
        except Exception:
            print('Error: please report issue to repo maintainer')
            return None
    
    return out