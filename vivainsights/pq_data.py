# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module returns a data frame containing a person query.
"""
import pkg_resources
import pandas as pd
import os

def load_pq_data():
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    # stream = pkg_resources.resource_stream(__name__, 'data/pq_data.csv')
    # stream = pkg_resources.resource_stream(__name__, os.path.join("..", "pq_data.csv"))
    # stream = pkg_resources.resource_string('vivainsights', 'data/pq_data.csv')
    if(pkg_resources.resource_exists(__name__, 'data/pq_data.csv')):
        stream = pkg_resources.resource_stream(__name__, 'data/pq_data.csv')
    elif(pkg_resources.resource_exists(__name__, '../data/pq_data.csv')):
        stream = pkg_resources.resource_stream(__name__, '../data/pq_data.csv')
    else:
        print('Error: please report issue to repo maintainer')    
    
    return pd.read_csv(stream, encoding='utf-8')