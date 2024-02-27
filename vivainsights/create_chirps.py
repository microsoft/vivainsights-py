# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import vivainsights as vi

def create_chirps(data: pd.DataFrame,
                  metrics: list,
                  hrvar: list = ["Organization", "SupervisorIndicator"],
                  min_group: int = 5,
                  bp = {},
                  return_type: str = 'table'):
    
    # 1. Trend test - 4 weeks vs 12 weeks -------------------------------------
    
    list_ts = vi.test_ts(data = data, metrics = metrics, hrvar = hrvar, min_group = min_group, bp = bp, return_type = 'headlines')
    
    # 2. Internal benchmark test ----------------------------------------------
    
    list_int_bm = vi.test_int_bm(data = data, metrics = metrics, hrvar = hrvar, min_group = min_group, return_type = 'headlines')
    
    # 3. Best practice test ---------------------------------------------------
    
    list_bp = vi.test_best_practice(data = data, metrics = metrics, hrvar = hrvar, bp = bp, return_type = 'headlines')
    
    # All the headlines -------------------------------------------------------
    
    list_headlines = [list_ts, list_int_bm, list_bp]

    all_headlines = pd.concat(list_headlines)
    
    total_n = data['PersonId'].nunique()
    all_headlines['prop_n'] = all_headlines['n'] / total_n
    
    # Interesting score -------------------------------------------------------
    # Output - return all the headlines - append the interesting score
    
    # If `TestType == 'Internal Benchmark'`, then multiply `Interest_Score` by 0.9
    all_headlines['Interest_Score'] = np.where(all_headlines['TestType'] == 'Internal Benchmark', all_headlines['Interest_Score'] * 0.9, all_headlines['Interest_Score'])
    
    # If `TestType == 'Best Practice'`, then multiply `Interest_Score` by 0.8
    all_headlines['Interest_Score'] = np.where(all_headlines['TestType'] == 'Best Practice', all_headlines['Interest_Score'] * 0.8, all_headlines['Interest_Score'])
    
    all_headlines['Interest_Score2'] = all_headlines['Interest_Score'] * all_headlines['prop_n']
    
    # `Interest_Score2_minmax` - min-max scaled score
    all_headlines['Interest_Score2_minmax'] = (all_headlines['Interest_Score2'] - all_headlines['Interest_Score2'].min()) / (all_headlines['Interest_Score2'].max() - all_headlines['Interest_Score2'].min())
    
    # Drop and rename columns
    all_headlines = all_headlines.drop(columns=['prop_n', 'Interest_Score', 'Interest_Score2'])
    all_headlines.rename(columns={'Interest_Score2_minmax': 'Interest_Score'}, inplace=True)   
    
    # Sort 'Interest_Score' in descending order
    all_headlines = all_headlines.sort_values(by='Interest_Score', ascending=False) 
    
    #TODO: headline selection in order to build a story
    # Interestingness: time trend > internal benchmark > best practice
    # Then build in rules for when best practice etc. may trump time trends (e.g. What makes a strong/weak trend?)    
    
    
    
    
    # Output - just the interesting headlines
    # Output - individual tables for each test 
    # Plot for each interesting headline
    
    # print(str(len(list_ts)) + ' number of data frame outputs from trend test')
    # print(str(len(list_int_bm)) + ' number of data frame outputs from internal benchmark test')
    # 
    # combined_list = list_ts + list_int_bm
    # return combined_list
    return all_headlines