# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module returns a data frame containing a person-to-person query.
"""
import pkg_resources
import pandas as pd
import os

def load_p2p_data():
    if(pkg_resources.resource_exists(__name__, 'data/p2p_data.csv')):
        stream = pkg_resources.resource_stream(__name__, 'data/p2p_data.csv')
    elif(pkg_resources.resource_exists(__name__, '../data/p2p_data.csv')):
        stream = pkg_resources.resource_stream(__name__, '../data/p2p_data.csv')
    else:
        print('Error: please report issue to repo maintainer')    
    
    # Address `ResourceWarning unclosed file` issue
    out = pd.read_csv(stream, encoding='utf-8')
    stream.close()
    
    return out