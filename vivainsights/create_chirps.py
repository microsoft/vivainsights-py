# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from datetime import timedelta
import vivainsights as vi
from scipy import stats

#TODO: EXCEPTIONS FOR FEWER THAN 12 MONTHS OF DATA
#TODO: PERSON METRICS IN ADDITION TO GROUP METRICS FOR 4MA VS 12MA
#TODO: WEIGHTS FOR INTERNAL BENCHMARKS

def test_ts(data: pd.DataFrame,
                  metrics: list,
                  hrvar: list = ["Organization", "SupervisorIndicator"],
                  min_group: int = 5):
    """
    This function takes in a DataFrame representing a Viva Insights person query and returns a list of DataFrames containing the results of the trend test.
    """    
    
    # Define date windows
    latest_date = data['MetricDate'].max()
    four_weeks_ago = latest_date - timedelta(weeks=4)
    twelve_weeks_ago = latest_date - timedelta(weeks=12)
    
    short_period = 4
    long_period = 12
    
    # Identify list of exception metrics where lower values and downward trends are notable
    exception_metrics = [
        'Meeting_hours_with_manager_1_on_1', 
        'Meetings_with_manager_1_on_1', 
        'Total_focus_hours'
    ]
        
    metric_columns = metrics
    ranking_order = {metric: 'low' if metric in exception_metrics else 'high' for metric in metric_columns}

    # Initialize an empty list for storing DataFrames
    grouped_data_list = []
    
    for each_hrvar in hrvar:
        
        for each_metric in metrics:
            
            # Initialize an empty DataFrame for group metrics
            group_metrics = data[['PersonId', 'MetricDate', each_hrvar, each_metric]].copy()
                        
            groups = data[each_hrvar].unique()
            dates = data['MetricDate'].unique()         
            
            # Group at a date-org level
            grouped_data = group_metrics.groupby(['MetricDate', each_hrvar]).agg({each_metric: 'mean', 'PersonId': 'nunique'}).reset_index()    
            grouped_data = grouped_data.rename(columns={'PersonId': 'n'})            
                        
            grouped_data['4_Period_MA_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].apply(lambda x: x.rolling(window=4, min_periods=1).mean()).reset_index(level=0, drop=True)
            grouped_data['12_Period_MA_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].apply(lambda x: x.rolling(window=12, min_periods=1).mean()).reset_index(level=0, drop=True)
            grouped_data['All_Time_Avg_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].apply(lambda x: x.rolling(window=52, min_periods=1).mean()).reset_index(level=0, drop=True)
        
            # 4MA flipping the 12MA
            grouped_data['Last_Week_4MA_' + each_metric] = grouped_data.groupby(each_hrvar)['4_Period_MA_' + each_metric].shift(1).reset_index(level=0, drop=True)
            grouped_data['4MA_Flipped_12MA_' + each_metric] = grouped_data.apply(
                lambda row: (row['4_Period_MA_' + each_metric] > row['12_Period_MA_' + each_metric] and 
                             row['Last_Week_4MA_' + each_metric] <= row['12_Period_MA_' + each_metric])
                if each_metric not in exception_metrics
                else (row['4_Period_MA_' + each_metric] < row['12_Period_MA_' + each_metric] and
                      row['Last_Week_4MA_' + each_metric] >= row['12_Period_MA_' + each_metric]), axis=1
            ).reset_index(level=0, drop=True)
            
            # Stdev
            grouped_data['Stdev_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].apply(lambda x: x.rolling(window=long_period, min_periods=1).std()).reset_index(level=0, drop=True)
            
            # Group rank
            order = ranking_order[each_metric] == 'high'
            grouped_data['Rank_' + each_metric] = grouped_data.groupby('MetricDate')[each_metric].rank(ascending=not order)
            grouped_data['4_Week_Avg_Rank_' + each_metric] = grouped_data.groupby(each_hrvar)['Rank_' + each_metric].transform(lambda x: x.rolling(window=4, min_periods=1).mean()).reset_index(level=0, drop=True)
            grouped_data['12_Week_Avg_Rank_' + each_metric] = grouped_data.groupby(each_hrvar)['Rank_' + each_metric].transform(lambda x: x.rolling(window=12, min_periods=1).mean()).reset_index(level=0, drop=True)
    
            grouped_data_list.append(grouped_data)
            
    return grouped_data_list

def test_int_bm(data: pd.DataFrame,
                  metrics: list,
                  hrvar: list = ["Organization", "SupervisorIndicator"],
                  min_group: int = 5):
    
    grouped_data_benchmark_list = []
    
    for each_metric in metrics:
        bm_data = vi.create_rank_calc(
            data,
            metric = each_metric,
            hrvar = hrvar,
            stats = True
        )

        #NOTE: Should this section be included as part of `create_rank_calc()`?        
        #NOTE: Calculations are needed to calculate n employees over threshold, potentially calling `create_inc_bar()` 
        
        # Append full population mean and sd
        bm_data['pop_mean_' + each_metric] = data[each_metric].mean()
        bm_data['pop_std_' + each_metric] = data[each_metric].std()
        bm_data['pop_n'] = data['PersonId'].nunique()

        # Perform the t-test and add the p-values to the DataFrame
        bm_data['p_value'] = bm_data.apply(lambda row: stats.ttest_ind_from_stats(
            mean1=row['metric'], std1=row['sd'], nobs1=row['n'],
            mean2=row['pop_mean_' + each_metric], std2=row['pop_std_' + each_metric], nobs2=row['pop_n']
        )[1], axis=1)

        # Add a column indicating whether the result is statistically significant
        alpha = 0.05  # Set your significance level
        bm_data['is_significant'] = bm_data['p_value'] < alpha

        # Add a column indicating the type of the test
        bm_data['test_type'] = 'Two-sample t-test'
        
        grouped_data_benchmark_list.append(bm_data)
    
    return grouped_data_benchmark_list


#TODO: NOT COMPLETE
def create_inc_bm(
    data: pd.DataFrame,
    metric: str,
    hrvar: str
):
    """
    This function calculates the number of employees who fall above and below the population average for a given metric. 
    """
    
    # Population average
    pop_mean = data[metric].mean()    
    pop_n = data['PersonId'].nunique()
    
    data_trans = data.copy()  
    
    conditions = [
        (data_trans[metric] > pop_mean),
        (data_trans[metric] < pop_mean),
        (data_trans[metric] == pop_mean)
    ]
    choices = ['above', 'below', 'equal']

    data_trans[metric + '_threshold'] = np.select(conditions, choices, default=np.nan)
    data_trans = data_trans.groupby([hrvar, metric + '_threshold'])['PersonId'].nunique().reset_index() 
    data_trans = data_trans.rename(columns={'PersonId': 'n'})
    
    # data_trans['group_n'] = data_trans.groupby(hrvar)['n'].sum().reset_index() #TODO: FIX THIS TO RETURN A ROW FOR EACH GROUP
    
    group_n = data_trans.groupby(hrvar)['n'].sum().reset_index()
    group_n.columns = [hrvar, 'group_n']

    data_trans = pd.merge(data_trans, group_n, on=hrvar)
      
    data_trans['pop_n'] = pop_n
    # data_trans['incidence'] = data_trans['n'] / data_trans['pop_n']
    
    data_trans['incidence'] = data_trans.groupby(hrvar).apply(lambda x: x['n'] / x['group_n']).reset_index(level=0, drop=True)
    
    return data_trans
    
    
#TODO: NOT COMPLETE
def create_chirps(data: pd.DataFrame,
                  metrics: list,
                  hrvar: list = ["Organization", "SupervisorIndicator"],
                  min_group: int = 5,
                  return_type: str = 'table'):
    
    # 1. Trend test - 4 weeks vs 12 weeks -------------------------------------
    
    list_ts = test_ts(data = data, metrics = metrics, hrvar = hrvar, min_group = min_group)
    
    # 2. Internal benchmark test ----------------------------------------------
    
    list_int_bm = test_int_bm(data = data, metrics = metrics, hrvar = hrvar, min_group = min_group)
    
    # 3. Best practice test ---------------------------------------------------
    
    # All the headlines -------------------------------------------------------
    
    # Interesting score -------------------------------------------------------
    
    # Output - return all the headlines - append the interesting score
    # Output - just the interesting headlines
    # Output - individual tables for each test 
    # Plot for each interesting headline
    
    print(str(len(list_ts)) + ' number of data frame outputs from trend test')
    print(str(len(list_int_bm)) + ' number of data frame outputs from internal benchmark test')
    
    combined_list = list_ts + list_int_bm
    return combined_list