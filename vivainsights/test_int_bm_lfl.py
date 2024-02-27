# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd
import vivainsights as vi
import numpy as np

def test_int_bm_lfl(
    data: pd.DataFrame,
    metrics: list,
    hrvar: list = ["Organization"],
    bm_hrvar: list = ["FunctionType", "SupervisorIndicator"],            
    min_group: int = 5,
    return_type: str = 'full'
):
    """
    Person-level means are compared with the like-for-like groups identified by HR attributes specified in the `bm_hrvar` list.
    
    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the data to be tested. Each row represents an observation and each column represents a variable.

    metrics : list
        The list of metrics to be tested. Each metric should correspond to a column name in `data`.
        
    hrvar : list, optional
        A list of variables to be iterated on for the like-for-like internal benchmark test. By default, the variables are 'Organization'.
        
    bm_hrvar : list, optional
        A list variables to be used to create the benchmark for the like-for-like internal benchmark test. 
        By default, the variables are 'FunctionType' and 'SupervisorIndicator'.
        This list cannot be empty and must be of maximum length 2.
    
    min_group : int, optional
        The minimum group size for the internal benchmark test. By default, the minimum group size is 5.
        
    return_type: str, optional
        The type of output to return. By default, the output is set to 'full'. Other options include 'headlines'.
        
    Examples
    --------
    >>> test_int_bm_lfl(
    data = vi.load_pq_data(),
    metrics = ['Collaboration_hours', 'After_hours_collaboration_hours'],
    hrvar = ['Organization'],
    bm_hrvar = ['FunctionType', 'SupervisorIndicator'],
    return_type = 'headlines'
    )
    """   
    
    list_int_bm_df = []
    grouped_data_list_headlines = []
    
    # `bm_hrvar` must be of length 2
    if len(bm_hrvar) > 2:
        raise ValueError('bm_hrvar must be of maximum length 2.')
    
    for each_metric in metrics:
        
        for each_hrvar in hrvar:
        
            intbm_str = 'InternalBenchmark_' + each_metric
            dintbm_str = 'DiffIntBench_' + each_metric
            pdintbm_str = 'PercDiffIntBench_' + each_metric
            
            p_df = vi.create_int_bm(
                data = data,
                metric = each_metric,
                hrvar = bm_hrvar
                )
            
            # List of values in 'hrvar' that are not in 'bm_hrvar'
            hrvar_diff = list(set(hrvar) - set(bm_hrvar))
            
            # Create an attribute dataset to join back to p_df
            attr_data = data[['PersonId', 'MetricDate'] + hrvar_diff]
            
            p_df = p_df.merge(attr_data, on = ['PersonId', 'MetricDate'], how = 'left')
            
            # Filter down to the latest date
            p_df = p_df.loc[p_df['MetricDate'] == p_df['MetricDate'].max()].copy()
            
            p_df = p_df.groupby(each_hrvar).agg({
                each_metric : 'mean',
                intbm_str : 'mean',
                'PersonId' : 'nunique'
            })
            
            p_df.rename(columns = {'PersonId': 'n'}, inplace = True)
    
            p_df[dintbm_str] = p_df[each_metric] - p_df[intbm_str]
            p_df[pdintbm_str] = p_df[dintbm_str] / p_df[intbm_str]
                
            p_df.reset_index(inplace = True)
                
            list_int_bm_df.append(p_df) 
            
            # Headlines -------------------------------------------------------            
            # Filter by interesting headlines only - at least 5% difference against internal benchmark
            grouped_data_headlines = p_df.loc[abs(p_df[pdintbm_str]) > 0.05].copy()
            
            # Add additional columns  
            grouped_data_headlines['TestType'] = 'Internal Benchmark II'
            grouped_data_headlines['Metric'] = each_metric
            grouped_data_headlines['Attribute'] = each_hrvar 
            grouped_data_headlines = grouped_data_headlines.rename(
                columns={
                    each_hrvar: 'AttributeValue',
                    each_metric: 'MetricValue'}
                )
            
            # Headlines
            grouped_data_headlines['Headlines'] = (
                'Employees with ' + each_hrvar + '==' + grouped_data_headlines['AttributeValue'].astype(str) +
                ' typically see ' + each_metric + ' (' + grouped_data_headlines['MetricValue'].round(1).astype(str) +
                np.where(grouped_data_headlines[pdintbm_str] >= 0,
                         ') higher than expected ',
                    ') lower than expected ') +
                '(' + (grouped_data_headlines[pdintbm_str] * 100).round(1).astype(str) +              
                '%) compared to employees with similar ' +
                bm_hrvar[0] + ' and ' + bm_hrvar[1] + ' ('+
                    grouped_data_headlines[intbm_str].round(1).astype(str) + ').'
                )
            
            # InterestScore - a min-max scaled score     
            grouped_data_headlines['Interest_Score'] = grouped_data_headlines[pdintbm_str]          
            min_score = grouped_data_headlines['Interest_Score'].min()
            max_score = grouped_data_headlines['Interest_Score'].max()

            if min_score == max_score:
                grouped_data_headlines['Interest_Score'] = 0
            else:
                grouped_data_headlines['Interest_Score'] = (grouped_data_headlines['Interest_Score'] - min_score) / (max_score - min_score)
                
            grouped_data_headlines = grouped_data_headlines[
                [
                'TestType',
                'Attribute',
                'AttributeValue',
                'Metric',
                'MetricValue',
                'n',
                'Headlines',
                'Interest_Score'
                ]
            ]
            
            grouped_data_list_headlines.append(grouped_data_headlines)
    
    # Conditional for return type 
    if return_type == 'full':
        return list_int_bm_df
    elif return_type == 'headlines':
        
        # Return row-bound DataFrame from list of headlines    
        headlines_df = pd.concat(grouped_data_list_headlines)
        
        # Sort 'Interest_Score' in descending order
        headlines_df = headlines_df.sort_values(by='Interest_Score', ascending=False)
        
        return headlines_df