
#--------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
                                            
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

def p_test(data, outcome, behavior, paired=False):
    # Filter the dataset based on the outcome variable
    train = data[data[outcome].isin([0, 1])].copy()

    # Convert outcome to string and then to a factor
    train[outcome] = train[outcome].astype(str).astype('category')
    p_value_dict={}
    for i in behavior:
    # Separate data into positive and negative outcomes
        pos = train[train[outcome] == '1'][i].dropna()
        neg = train[train[outcome] == '0'][i].dropna()
    
        # Ensure that the lengths of pos and neg are the same
        min_len = min(len(pos), len(neg))
        pos = pos[:min_len]
        neg = neg[:min_len]
    
        # Perform Wilcoxon signed-rank test (or rank-sum test for unpaired data)
        _, p_value = wilcoxon(pos, neg) if paired else wilcoxon(pos, neg, alternative='two-sided')
        p_value_dict.update({i:p_value})

    data_frame=pd.DataFrame(list(p_value_dict.items()), columns=['Variable', 'pval'])

    return data_frame