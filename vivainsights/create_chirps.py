# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from datetime import timedelta
import vivainsights as vi
from scipy import stats
import re 
import matplotlib.pyplot as plt

def test_ts(data: pd.DataFrame,
                  metrics: list,
                  hrvar: list = ["Organization", "SupervisorIndicator"],
                  min_group: int = 5,
                  bp: dict = {},
                  return_type: str = 'full'):
    """
    This function takes in a DataFrame representing a Viva Insights person query and returns a list of DataFrames containing the results of the trend test.
    
    The function identifies the latest date in the data, and defines two periods: the last four weeks and the last twelve weeks. 
    
    It then initializes a list of exception metrics where lower values and downward trends are notable. 

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the data to be tested. Each row represents an observation and each column represents a variable.

    metrics : list
        The list of metrics to be tested. Each metric should correspond to a column name in `data`.

    hrvar : list, optional
        A list of variables to be used in the `vi.create_rank_calc` function. By default, the variables are 'Organization' and 'SupervisorIndicator'.

    min_group : int, optional
        The minimum group size for the trend test. By default, the minimum group size is 5.

    Returns
    -------
    list
        A list of DataFrames. Each DataFrame contains the results of the trend test for one metric. The DataFrame includes the original data, the p-value of the trend test, and a boolean column indicating whether the result is statistically significant at the 0.05 level.
    """    
    
    # Count number of unique dates in `MetricDate`
    # If fewer than 12 unique values, return an error message
    if data['MetricDate'].nunique() < 12:
        return 'Error: fewer than 12 unique dates in `MetricDate`'  
    
    # Message if fewer than 52 weeks of data available
    if data['MetricDate'].nunique() < 52:
        print('Note: using only ' + str(data['MetricDate'].nunique()) + ' weeks of data when calculating all time average')
    
    # If keys in key-value pairs in `bp` dictionary do not match those in `metrics`, return an error message
    if set(bp.keys()) != set(metrics):
        return 'Error: keys in `bp` dictionary do not match those in `metrics`'    
    
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
            
            # Filter by minimum group size
            grouped_data = grouped_data[grouped_data['n'] >= min_group]      
            
            # Order by MetricDate (ascending)
            grouped_data = grouped_data.sort_values('MetricDate', ascending = True)
                        
            # Calculate moving averages                        
            grouped_data['4_Period_MA_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].apply(lambda x: x.rolling(window=4, min_periods=1).mean()).reset_index(level=0, drop=True)
            grouped_data['12_Period_MA_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].apply(lambda x: x.rolling(window=12, min_periods=1).mean()).reset_index(level=0, drop=True)
            grouped_data['All_Time_Avg_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].apply(lambda x: x.rolling(window=52, min_periods=1).mean()).reset_index(level=0, drop=True)
        
            # Calculate cumulative increases / decreases
            grouped_data['Diff_' + each_metric] = grouped_data[each_metric].diff() # Difference between current and previous value
            grouped_data['SignDiff_' + each_metric] = np.sign(grouped_data['Diff_' + each_metric])
            
            # grouped_data['SignDiff_' + each_metric] = np.where(np.sign(grouped_data['Diff_' + each_metric].abs() > 0), grouped_data['Diff_' + each_metric], 0) # Sign of the difference
            grouped_data['SignChange_' + each_metric] = grouped_data['SignDiff_' + each_metric].ne(grouped_data['SignDiff_' + each_metric].shift()).cumsum()
            grouped_data['CumIncrease_' + each_metric] = grouped_data.groupby('SignChange_' + each_metric).cumcount().where(grouped_data['SignDiff_' + each_metric] == 1, 0)
            grouped_data['CumDecrease_' + each_metric] = grouped_data.groupby('SignChange_' + each_metric).cumcount().where(grouped_data['SignDiff_' + each_metric] == -1, 0)        
        
            # Interest Test #1: Does 4MA exceed threshold value? 
            if each_metric not in bp.keys():
               grouped_data['Test1_4MA_Exceed_Threshold_' + each_metric] = False
            else:
                grouped_data['Test1_4MA_Exceed_Threshold_' + each_metric] = (grouped_data['4_Period_MA_' + each_metric] > bp[each_metric]).reset_index(level=0, drop=True)
            
            # Interest Test #2: does the 4MA exceed the 12MA, indicating that the metric is trending upwards?
            # 4MA flipping the 12MA
            grouped_data['Last_Week_4MA_' + each_metric] = grouped_data.groupby(each_hrvar)['4_Period_MA_' + each_metric].shift(1).reset_index(level=0, drop=True)
            grouped_data['Test2_4MA_Flipped_12MA_' + each_metric] = grouped_data.apply(
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
            
            # Interest Test #3: Current value is closer to the 4MA than the 12MA
            grouped_data['Diff_Current_4MA' + each_metric] = abs(grouped_data[each_metric] - grouped_data['4_Period_MA_' + each_metric])
            grouped_data['Diff_Current_12MA' + each_metric] = abs(grouped_data[each_metric] - grouped_data['12_Period_MA_' + each_metric])
            grouped_data['Test3_Diff_Current_4MA_Over_12MA_' + each_metric] = (grouped_data['Diff_Current_4MA' + each_metric] > grouped_data['Diff_Current_12MA' + each_metric]).reset_index(level=0, drop=True)
            
            # Interest Test #4: Current value exceeds the 52 week average
            if data['MetricDate'].nunique() < 52:
                grouped_data['Test4_Current_Exceed_52Wk_Avg_' + each_metric] = False
            else:
                grouped_data['Test4_Current_Exceed_52Wk_Avg_' + each_metric] = (grouped_data[each_metric] > grouped_data['All_Time_Avg_' + each_metric]).reset_index(level=0, drop=True)
            
            # Interest Test #5: Current value does not exceed the 4MA by >2 stdev (not a spike)
            grouped_data['Test5_Current_LessThan_4MA_2Stdev_' + each_metric] = (
                grouped_data[each_metric] < (grouped_data['4_Period_MA_' + each_metric] + 2 * grouped_data['Stdev_' + each_metric])
                ).reset_index(level=0, drop=True)          
            
            # Interest Test #6: Current value against 4MA and 12MA
            grouped_data['DiffP_Current_4MA' + each_metric] = (grouped_data[each_metric] - grouped_data['4_Period_MA_' + each_metric]) / grouped_data['4_Period_MA_' + each_metric]
            grouped_data['DiffP_Current_12MA' + each_metric] = (grouped_data[each_metric] - grouped_data['12_Period_MA_' + each_metric]) / grouped_data['12_Period_MA_' + each_metric]
            grouped_data['DiffP_Total'] = abs(grouped_data['DiffP_Current_4MA' + each_metric]) + abs(grouped_data['DiffP_Current_12MA' + each_metric])
            grouped_data['Test6_DiffP_Total_IsLarge'] = (grouped_data['DiffP_Total'] > 0.5).reset_index(level=0, drop=True)            
            
            # Interest Test #7: Cumulative increases and decreases            
            grouped_data['Test7_CumChange4Weeks_' + each_metric] = ((grouped_data['CumIncrease_' + each_metric] > 4) | (grouped_data['CumDecrease_' + each_metric] > 4)).reset_index(level=0, drop=True)
            
            # Reorder columns
            cols = grouped_data.columns.tolist()
            test_cols = [col for col in cols if re.match(r'Test[0-9]_', col)]
            other_cols = [col for col in cols if not re.match(r'Test[0-9]_', col)]
            new_order_cols = other_cols + test_cols
            grouped_data = grouped_data[new_order_cols]
            
            # Calculate Interest Score from tests
            # Sum rowwise from all columns that start with 'Test_'
            grouped_data['Interest_Score'] = grouped_data[[col for col in grouped_data.columns if re.match(r'Test[0-9]_', col)]].sum(axis=1)
            
            # Conditional for return type 
            if return_type == 'full':
                
                grouped_data_list.append(grouped_data)
                
                return grouped_data_list
                
            elif return_type == 'consec_weeks':

                # Initialize empty list for storing consecutive weeks
                list_consec_weeks = []
                
                for each_group in groups:
                    # Filter the DataFrame for the specific group
                    each_df = grouped_data[grouped_data[each_hrvar] == each_group]
                    # Sort the data by date in descending order
                    each_df = each_df.sort_values('MetricDate', ascending = False)
                    consecutive_weeks = 0
                    for _, row in each_df.iterrows():
                        if row[f'4MA_Flipped_12MA_{each_metric}'] == True:
                            consecutive_weeks += 1
                        else:
                            break
                    list_consec_weeks.append(consecutive_weeks)
                
                consec_weeks_df = pd.DataFrame({
                    each_hrvar: groups,
                    'Consecutive_Weeks': list_consec_weeks
                })
                
                grouped_data_list.append(consec_weeks_df)
                
                return grouped_data_list
            
            elif return_type == 'plot':
                
                for each_group in groups:
                
                    grouped_data_filt = grouped_data[grouped_data[each_hrvar] == each_group]
                
                    plt.figure(figsize=(10, 6))
                    plt.plot(grouped_data_filt['MetricDate'], grouped_data_filt[each_metric], label = each_metric)
                    plt.plot(grouped_data_filt['MetricDate'], grouped_data_filt['4_Period_MA_' + each_metric], label = '4_Period_MA_' + each_metric)
                    plt.plot(grouped_data_filt['MetricDate'], grouped_data_filt['12_Period_MA_' + each_metric], label = '12_Period_MA_' + each_metric)
                    plt.xlabel('MetricDate')
                    plt.ylabel(each_metric)
                    plt.suptitle(each_metric + ' over time', fontsize=14, fontweight='bold')
                    plt.title(str(each_hrvar) + ': ' + str(each_group), fontsize=10)
                    plt.ylim(bottom=0)  # Set the start of y-axis to 0
                    plt.legend()
                    plt.show()              
                
            else:
                print('Error: invalid return type')

def test_int_bm(data: pd.DataFrame,
                metrics: list,
                hrvar: list = ["Organization", "SupervisorIndicator"],
                bm_data: pd.DataFrame = None,
                min_group: int = 5):
    """
    Performs an internal benchmark test on each metric and HR variable combination in the provided DataFrame.

    The function calculates the mean, standard deviation, and number of unique employees for each group and for the entire population. 
    It also calculates Cohen's d, a measure of effect size.

    A list of data frames is returned.

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
    
    return grouped_data_benchmark_list

def test_best_practice(
    data: pd.DataFrame,
    metrics: list,
    hrvar: list,
    bp: dict = {}
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

    Returns
    -------
    list
        A list of DataFrames. Each DataFrame contains the results of the best practice test for one metric. The DataFrame includes the original data, the benchmark mean, and the percentage difference between the population mean and the benchmark.
    
    """
    
    # If keys in key-value pairs in `bp` dictionary do not match those in `metrics`, return an error message
    if set(bp.keys()) != set(metrics):
        return 'Error: keys in `bp` dictionary do not match those in `metrics`'    
    
    grouped_data_benchmark_list = []
    
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
            bm_data = bm_data[bm_data['n'] >= 5]

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
            bm_data['perc_diff_mean'] = (bm_data['group_mean_' + each_metric] - bp_mean) / bm_data['group_mean_' + each_metric]
            
            grouped_data_benchmark_list.append(bm_data)
        
    return grouped_data_benchmark_list    
    
#TODO: NOT COMPLETE
def create_chirps(data: pd.DataFrame,
                  metrics: list,
                  hrvar: list = ["Organization", "SupervisorIndicator"],
                  min_group: int = 5,
                  return_type: str = 'table'):
    
    # 1. Trend test - 4 weeks vs 12 weeks -------------------------------------
    
    list_ts = test_ts(data = data, metrics = metrics, hrvar = hrvar, min_group = min_group)
    
    list_ts_flipped = []
    
    for i in list_ts:
        # Extract column name from `list_ts[i]` that matches '4MA_Flipped_12MA'        
        match = re.match('4MA_Flipped_12MA', list_ts[i].columns)
        filt_df = list_ts[i][list_ts[i][match] == True]
        list_ts_flipped.append(filt_df)   
    
    # 2. Internal benchmark test ----------------------------------------------
    
    list_int_bm = test_int_bm(data = data, metrics = metrics, hrvar = hrvar, min_group = min_group)
    
    # 3. Best practice test ---------------------------------------------------
    
    list_bp = test_best_practice(data = data, metrics = metrics, hrvar = hrvar, bp = {'Email_hours': 10})
    
    # All the headlines -------------------------------------------------------
    
    #TODO: headline selection in order to build a story
    # Interestingness: time trend > internal benchmark > best practice
    # Then build in rules for when best practice etc. may trump time trends (e.g. What makes a strong/weak trend?)    
    
    # Interesting score -------------------------------------------------------
    
    # Output - return all the headlines - append the interesting score
    # Output - just the interesting headlines
    # Output - individual tables for each test 
    # Plot for each interesting headline
    
    # print(str(len(list_ts)) + ' number of data frame outputs from trend test')
    # print(str(len(list_int_bm)) + ' number of data frame outputs from internal benchmark test')
    # 
    # combined_list = list_ts + list_int_bm
    # return combined_list
    return list_ts_flipped