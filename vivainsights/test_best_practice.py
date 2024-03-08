# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np

def test_best_practice(
    data: pd.DataFrame,
    metrics: list,
    hrvar: list,
    bp: dict = {},
    min_group: int = 5,
    return_type: str = 'full'
):
    """
    Takes in a DataFrame representing a Viva Insights person query and returns a list of DataFrames containing the results of the best practice test.
    
    The function adds the percentage difference between the population mean and the benchmark to the DataFrame for each metric.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the data to be tested. Each row represents an observation and each column represents a variable.

    metrics : list
        The list of metrics to be tested. Each metric should correspond to a column name in `data`.

    hrvar : list
        A list of variables to be used in the `vi.create_rank_calc` function.

    bp : dict, optional
        A dictionary containing the benchmark mean for each metric. The keys should correspond to the metric names and the values should be the benchmark means. By default, the benchmark mean for 'Emails_sent' is set to 10.

    min_group : int
        The minimum group size for the best practice test. By default, the minimum group size is 5.

    return_type: str
        The type of output to return. By default, the output is set to 'full'.

    Returns
    -------
    list
        A list of DataFrames. Each DataFrame contains the results of the best practice test for one metric. The DataFrame includes the original data, the benchmark mean, and the percentage difference between the population mean and the benchmark.
    
    """
    
    # If keys in key-value pairs in `bp` dictionary do not match those in `metrics`, return an error message
    if set(bp.keys()) != set(metrics):
        print('Warning: keys in `bp` dictionary do not match those in `metrics`. Only matched metrics will be calculated.') 
        metrics = list(bp.keys())
    
    grouped_data_benchmark_list = []
    grouped_data_list_headlines = []
    
    for each_hrvar in hrvar:
    
        for each_metric in metrics:
            
            bm_data = data.copy()
            
            pop_n = bm_data['PersonId'].nunique()
            
            # Extract best practice 'mean' from dictionary
            bp_mean = bp[each_metric]
            
            # Calculate person averages
            bm_data = bm_data.groupby(['PersonId', each_hrvar])[each_metric].mean().reset_index()
            
            # Set conditions
            conditions = [
                (bm_data[each_metric] > bp_mean),
                (bm_data[each_metric] < bp_mean),
                (bm_data[each_metric] == bp_mean)
            ]
            choices = ['above', 'below', 'equal']
            
            # Count of employees above/below threshold
            bm_data[each_metric + '_threshold'] = np.select(conditions, choices, default=np.nan)        
            bm_data = bm_data.groupby([each_hrvar, each_metric + '_threshold'])['PersonId'].nunique().reset_index() 
            bm_data = bm_data.rename(columns={'PersonId': 'n'})
            
            # Filter by minimum group size
            bm_data = bm_data[bm_data['n'] >= min_group]

            # Attach best practice 'mean' to each row
            bm_data['best_practice'] = bp_mean
            
            # Calculate group means (disregarding thresholds)
            data_trans = data.copy() 
            group_data = data_trans.groupby([each_hrvar, 'PersonId']).agg({each_metric: 'mean'}).reset_index()
            
            # calculate both group mean and unique PersonId (n)
            group_data = group_data.groupby(each_hrvar).agg({each_metric: 'mean', 'PersonId': 'nunique'}).reset_index()
            
            # Rename columns    
            group_data = group_data.rename(columns={each_metric: 'group_mean_' + each_metric})
            group_data = group_data.rename(columns={'PersonId': 'group_n'})
            
            # Join group averages to the benchmark data
            bm_data = pd.merge(bm_data, group_data, on = each_hrvar, how='left')
            
            bm_data['percent_of_pop'] = bm_data['n'] / bm_data['group_n']
                     
            # Calculate percentage difference from benchmark mean
            bm_data['perc_diff_mean'] = (bm_data['group_mean_' + each_metric] - bp_mean) / bp_mean
            
            grouped_data_benchmark_list.append(bm_data)
            
            # Headlines -------------------------------------------------------            
            # Filter by interesting headlines only - at least 50% difference against best practice
            grouped_data_headlines = bm_data.loc[abs(bm_data['perc_diff_mean']) >= 0.5].copy()
            
            # Only show headlines for 'above'
            grouped_data_headlines = grouped_data_headlines[grouped_data_headlines[each_metric + '_threshold'] == 'above']
            
            # Generate headlines        
            grouped_data_headlines['Headlines'] = (
                'For ' + each_hrvar + '==' + grouped_data_headlines[each_hrvar].astype(str) + ', ' +
                (grouped_data_headlines['percent_of_pop'] * 100).round(1).astype(str) + '% of the group has ' +
                each_metric + ' ' + grouped_data_headlines[each_metric + '_threshold'] + ' the best practice of ' +
                grouped_data_headlines['best_practice'].astype(str) + '. The group mean is ' +
                grouped_data_headlines['group_mean_' + each_metric].round(1).astype(str) +  ' (' +
                (grouped_data_headlines['perc_diff_mean'] * 100).round(1).astype(str) + '% vs best practice).'                
            )
            
            grouped_data_headlines['Attribute'] = each_hrvar
            grouped_data_headlines['Metric'] = each_metric
            grouped_data_headlines = grouped_data_headlines.rename(
                columns={
                    each_hrvar: 'AttributeValue',
                    'group_mean_' + each_metric: 'MetricValue'}
                )
            
            grouped_data_headlines['TestType'] = 'Best Practice'
            
            # Interest score - min-max scaled using `percent_of_pop`
            min_percent_of_pop = grouped_data_headlines['percent_of_pop'].min()
            max_percent_of_pop = grouped_data_headlines['percent_of_pop'].max()

            if min_percent_of_pop == max_percent_of_pop:
                grouped_data_headlines['Interest_Score'] = 0
            else:
                grouped_data_headlines['Interest_Score'] = (grouped_data_headlines['percent_of_pop'] - min_percent_of_pop) / (max_percent_of_pop - min_percent_of_pop)
            
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