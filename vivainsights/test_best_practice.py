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
        The DataFrame containing the Person Query data to run the data on. 
        The Person Query should be grouped at a weekly level, and must contain the columns `PersonId` and `MetricDate`.

    metrics : list, optional
        A list of metrics to be included in the analysis. Defaults to None.
        Each metric should correspond to a column name in `data`.

    hrvar : list
        A list of the HR or organizational variables to group by when computing headline metrics.  
        Defaults to `['Organization', 'SupervisorIndicator']`.

    bp : dict
        A dictionary containing the benchmark mean for each metric and the directionality of the threshold.  
        `bp` requires a two-level nested dictionary where the first level consists of two explicit keys: 'above' and 'below'.
        Each of these keys maps to a second-level dictionary, which contains its own set of key-value pairs.
        The keys in the second-level dictionaries represent metrics, and the values represent the corresponding thresholds
        The keys should correspond to the metric names and the values should be the benchmark means. 

    min_group : int, optional
        The minimum group size set for privacy. Defaults to 5.
        Groups with fewer people than `min_group` will not be included in the analysis.

    return_type: str
        The type of output to return. By default, the output is set to 'full'.

    Returns
    -------
    list
        A list of DataFrames. Each DataFrame contains the results of the best practice test for one metric. The DataFrame includes the original data, the benchmark mean, and the percentage difference between the population mean and the benchmark.
    
    """
    
    # If `bp` hasn't got a key for 'above', or 'below', create an empty key
    bp.setdefault('above', {})
    bp.setdefault('below', {})
    
    # set of unique metrics across 'above' and 'below'
    combined_keys = set(bp["above"].keys()) | set(bp["below"].keys())
    
    # If keys in key-value pairs in `bp` dictionary do not match those in `metrics`, return an error message
    if combined_keys != set(metrics):
        print('Warning: keys in `bp` dictionary do not match those in `metrics`. Only matched metrics will be calculated.') 
        metrics = list(combined_keys)
    
    grouped_data_benchmark_list = []
    grouped_data_list_headlines = []
    
    for each_hrvar in hrvar:
    
        for each_metric in metrics:            
            
            # Start of section where only 'above' or 'below' means are extracted
            
            bm_data_above = calc_bp_diff(
                data = data,
                bp = bp,
                direction = 'above',
                metric = each_metric,
                hrvar = each_hrvar,
                min_group = min_group
            )
            
            bm_data_below = calc_bp_diff(
                data = data,
                bp = bp,
                direction = 'below',
                metric = each_metric,
                hrvar = each_hrvar,
                min_group = min_group
            )
                
            # row-bind 'above' and 'below' data
            bm_data = pd.concat([bm_data_above, bm_data_below])                
            
            grouped_data_benchmark_list.append(bm_data)
            
            # Headlines -------------------------------------------------------            
            # Filter by interesting headlines only - at least 50% difference against best practice
            grouped_data_headlines = bm_data.loc[abs(bm_data['perc_diff_mean']) >= 0.5].copy()
            
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
            
            # return grouped_data_headlines
            
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
        
        
def calc_bp_diff(
    data: pd.DataFrame,
    bp: dict,
    direction: str,
    metric: str,
    hrvar: str,
    min_group: int):
    """
    Calculates the percentage of employees above or below the benchmark mean for a given metric.

    Returns a DataFrame with the following columns:
    - [hrvar]: the HR variable
    - [metric]_threshold: whether the group mean is above or below the benchmark mean
    - n: the number of employees in the group
    - best_practice: the benchmark mean
    - group_mean_[metric]: the group mean for the metric
    - group_n: the number of employees in the group
    - percent_of_pop: the percentage of the population in the group
    - perc_diff_mean: the percentage difference between the group mean and the benchmark mean
    
    """
    
    # Check if bp[direction][metric] exists - if not, return an empty DataFrame
    if metric not in bp[direction]:
        return pd.DataFrame()    
    
    bm_data = data.copy()
            
    pop_n = bm_data['PersonId'].nunique()

    # Calculate person averages
    bm_data = bm_data.groupby(['PersonId', hrvar])[metric].mean().reset_index()
        
    # Create groupings based on direction
    if direction == "above":

        bp_mean = bp['above'][metric]       
        
        conditions = [
            (bm_data[metric] > bp_mean),
            (bm_data[metric] <= bp_mean)
        ]
        choices = ['above', 'below or equal to']
    
    elif direction == "below":        
       
        bp_mean = bp['below'][metric]   

        conditions = [
            (bm_data[metric] < bp_mean),
            (bm_data[metric] >= bp_mean)
        ]
        choices = ['below', 'above or equal to']
    
    else:
        raise ValueError("direction must be 'above' or 'below'")

    # Count of employees above/below threshold
    bm_data[metric + '_threshold'] = np.select(conditions, choices, default=np.nan)        
    bm_data = bm_data.groupby([hrvar, metric + '_threshold'])['PersonId'].nunique().reset_index() 
    bm_data = bm_data.rename(columns={'PersonId': 'n'})
    
    # Filter by `direction` where it must only be equal to 'above' or 'below'
    bm_data = bm_data[bm_data[metric + '_threshold'] == direction]
    
    # Filter by minimum group size
    bm_data = bm_data[bm_data['n'] >= min_group]
    
    # Attach best practice 'mean' to each row
    bm_data['best_practice'] = bp_mean

    # Calculate group means (disregarding thresholds)
    data_trans = data.copy() 
    group_data = data_trans.groupby([hrvar, 'PersonId']).agg({metric: 'mean'}).reset_index()
    
    # calculate both group mean and unique PersonId (n)
    group_data = group_data.groupby(hrvar).agg({metric: 'mean', 'PersonId': 'nunique'}).reset_index()
    
    # Rename columns    
    group_data = group_data.rename(columns={metric: 'group_mean_' + metric})
    group_data = group_data.rename(columns={'PersonId': 'group_n'})
    
    # Join group averages to the benchmark data
    bm_data = pd.merge(bm_data, group_data, on = hrvar, how='left')
    
    bm_data['percent_of_pop'] = bm_data['n'] / bm_data['group_n']
             
    # Calculate percentage difference from benchmark mean
    bm_data['perc_diff_mean'] = (bm_data['group_mean_' + metric] - bp_mean) / bp_mean

    return bm_data