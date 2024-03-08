# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import vivainsights as vi

def test_int_bm(data: pd.DataFrame,
                metrics: list,
                hrvar: list = ["Organization", "SupervisorIndicator"],
                bm_data: pd.DataFrame = None,                
                min_group: int = 5,
                return_type: str = 'full'
                ):
    """
    Performs an internal benchmark test on each metric and HR variable combination in the provided DataFrame.

    The function calculates the mean, standard deviation, and number of unique employees for each group and for the entire population. 
    It also calculates Cohen's d, a measure of effect size.
    
    There are two options for calculating internal benchmarks:
    1. If `bm_data` is provided, the person-level means are compared with the population average is calculated from the `bm_data` DataFrame.
    2. If neither is provided, the person-level means are simply compared with the population average supplied in `data`. 

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the data to be tested. Each row represents an observation and each column represents a variable.

    metrics : list
        The list of metrics to be tested. Each metric should correspond to a column name in `data`.

    hrvar : list, optional
        A list of variables to be used in the `vi.create_rank_calc` function. By default, the variables are 'Organization' and 'SupervisorIndicator'.
        
    bm_data : pd.DataFrame, optional
        An optional DataFrame representing the population to be used for calculating the population average. If not provided, the population average is calculated from the `data` DataFrame.

    min_group : int, optional
        The minimum group size for the internal benchmark test. By default, the minimum group size is 5.
        
    return_type: str, optional
        The type of output to return. By default, the output is set to 'full'.
        
    Returns
    -------
    list
        A list of DataFrames. Each DataFrame contains the results of the internal benchmark test for one metric. The DataFrame includes the original data, the group and population statistics, and Cohen's d:
        - the mean, standard deviation, and number of employees for each group
        - the population mean and standard deviation for each metric
        - Cohen's d, a measure of effect size

    Notes
    -----
    The function uses the `vi.create_rank_calc` function to calculate the rank for each metric. It also appends the full population mean, standard deviation, and number of unique employees to the DataFrame. Cohen's d is calculated as the difference between the group mean and the population mean, divided by the pooled standard deviation.
    """
    
    grouped_data_benchmark_list = []
    grouped_data_list_headlines = []
    
    for each_metric in metrics:
        ranked_data = vi.create_rank_calc(
            data,
            metric = each_metric,
            hrvar = hrvar,
            stats = True
        )        
        
        # Population average
        if bm_data is not None:
            pop_mean = bm_data[each_metric].mean()  
            pop_std = bm_data[each_metric].std()
            pop_n = bm_data['PersonId'].nunique()
        else:
            pop_mean = data[each_metric].mean()    
            pop_std = data[each_metric].std()
            pop_n = data['PersonId'].nunique()
        
        # Filter by minimum group size
        ranked_data = ranked_data[ranked_data['n'] >= min_group]
        
        # Append full population mean and sd
        ranked_data['pop_mean_' + each_metric] = pop_mean
        ranked_data['pop_std_' + each_metric] = pop_std
        ranked_data['pop_n'] = pop_n
        
        # Percentage difference against benchmark
        ranked_data['perc_diff'] = (ranked_data['metric'] - pop_mean) / ranked_data['metric']

        # Calculate Cohen's d between means of group and benchmark population
        # the magnitude of the difference between two means in terms of standard deviation units
        # d = (M1 - M2) / sqrt((s1^2 + s2^2) / 2)
        ranked_data['cohen_d'] = (ranked_data['metric'] - ranked_data['pop_mean_' + each_metric]) / np.sqrt((ranked_data['sd'] ** 2 + ranked_data['pop_std_' + each_metric] ** 2) / 2)
        
        grouped_data_benchmark_list.append(ranked_data)
    
        # Headlines -------------------------------------------------------            
        # Filter by interesting headlines only - at least a medium effect (d >= 0.5)
        grouped_data_headlines = ranked_data.loc[ranked_data['cohen_d'] >= 0.5].copy()
        
        # Generate headlines        
        grouped_data_headlines['Headlines'] = (
            'For ' + grouped_data_headlines['hrvar'] + '==' + grouped_data_headlines['attributes'].astype(str) +
            ', ' + each_metric + ' (' + grouped_data_headlines['metric'].round(1).astype(str) + ') is ' +
            (grouped_data_headlines['perc_diff'] * 100).round(1).astype(str) + '%' +
            np.where(grouped_data_headlines['perc_diff'] >= 0,
                    ' higher than the benchmark population average ',
                    ' lower than the benchmark population average ') +
            grouped_data_headlines['pop_mean_' + each_metric].round(1).astype(str) +
            #+ ' with a Cohen\'s d of ' +
            #grouped_data_headlines['cohen_d'].round(1).astype(str) 
            '.'
        )
        
        grouped_data_headlines['TestType'] = 'Internal Benchmark'
        grouped_data_headlines['Metric'] = each_metric
                
        grouped_data_headlines = grouped_data_headlines.rename(
            columns={'hrvar': 'Attribute',
                     'attributes': 'AttributeValue',
                     'metric': 'MetricValue'}
            )

        # Interest Score - min-max scaled
        min_cohen_d = grouped_data_headlines['cohen_d'].min()
        max_cohen_d = grouped_data_headlines['cohen_d'].max()

        if min_cohen_d == max_cohen_d:
            grouped_data_headlines['Interest_Score'] = 0
        else:
            grouped_data_headlines['Interest_Score'] = (grouped_data_headlines['cohen_d'] - min_cohen_d) / (max_cohen_d - min_cohen_d)
        
        # Clean up and reorder columns
        grouped_data_headlines = grouped_data_headlines[['TestType', 'Attribute', 'AttributeValue', 'Metric', 'MetricValue', 'n', 'Headlines', 'Interest_Score']]
            
        # Sort 'Interest_Score' in descending order
        grouped_data_headlines = grouped_data_headlines.sort_values(by='Interest_Score', ascending=False)    
            
        grouped_data_list_headlines.append(grouped_data_headlines)

    if return_type == 'full':
        
        return grouped_data_benchmark_list
    
    elif return_type == 'headlines':    
        
        if not grouped_data_list_headlines: # empty list
            
            return pd.DataFrame()  # return an empty DataFrame
        
        else:
            # Return row-bound DataFrame from list of headlines    
            headlines_df = pd.concat(grouped_data_list_headlines)
            
            # Sort 'Interest_Score' in descending order
            headlines_df = headlines_df.sort_values(by='Interest_Score', ascending=False)
            
            return headlines_df