# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module returns a data frame containing a group-to-group query.

Example
-------
>>> import vivainsights as vi
>>> g2g_data = vi.load_g2g_data()
"""
import pkg_resources
import pandas as pd
import os

def load_g2g_data():
    if(pkg_resources.resource_exists(__name__, 'data/g2g_data.csv')):
        stream = pkg_resources.resource_stream(__name__, 'data/g2g_data.csv')
    elif(pkg_resources.resource_exists(__name__, '../data/g2g_data.csv')):
        stream = pkg_resources.resource_stream(__name__, '../data/g2g_data.csv')
    else:
        print('Error: please report issue to repo maintainer')    
    
    # Address `ResourceWarning unclosed file` issue
    out = pd.read_csv(stream, encoding='utf-8')
    stream.close()
    
    return out