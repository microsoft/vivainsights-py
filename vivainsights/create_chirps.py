# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from datetime import timedelta
import vivainsights as vi
from scipy import stats

#TODO: WEIGHTS FOR INTERNAL BENCHMARKS

def test_ts(data: pd.DataFrame,
                  metrics: list,
                  hrvar: list = ["Organization", "SupervisorIndicator"],
                  min_group: int = 5):
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

            # Filter by minimum group size
            grouped_data = grouped_data[grouped_data['n'] >= min_group]
            
            grouped_data_list.append(grouped_data)
            
    return grouped_data_list

def test_int_bm(data: pd.DataFrame,
                  metrics: list,
                  hrvar: list = ["Organization", "SupervisorIndicator"],
                  min_group: int = 5):
    """
    Performs an internal benchmark test on each metric and HR variable combination in the provided DataFrame.

    The function calculates the mean, standard deviation, and number of unique employees for each group and for the entire population. It also calculates Cohen's d, a measure of effect size.

    A list of data frames is returned.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the data to be tested. Each row represents an observation and each column represents a variable.

    metrics : list
        The list of metrics to be tested. Each metric should correspond to a column name in `data`.

    hrvar : list, optional
        A list of variables to be used in the `vi.create_rank_calc` function. By default, the variables are 'Organization' and 'SupervisorIndicator'.

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
        bm_data = vi.create_rank_calc(
            data,
            metric = each_metric,
            hrvar = hrvar,
            stats = True
        )

        #NOTE: Should this section be included as part of `create_rank_calc()`?        
        #NOTE: Calculations are needed to calculate n employees over threshold, potentially calling `create_inc_bar()` 
        
        # Filter by minimum group size
        bm_data = bm_data[bm_data['n'] >= min_group]
        
        # Append full population mean and sd
        bm_data['pop_mean_' + each_metric] = data[each_metric].mean()
        bm_data['pop_std_' + each_metric] = data[each_metric].std()
        bm_data['pop_n'] = data['PersonId'].nunique()

        # Calculate Cohen's d between means of group and benchmark population
        # the magnitude of the difference between two means in terms of standard deviation units
        # d = (M1 - M2) / sqrt((s1^2 + s2^2) / 2)
        bm_data['cohen_d'] = (bm_data['metric'] - bm_data['pop_mean_' + each_metric]) / np.sqrt((bm_data['sd'] ** 2 + bm_data['pop_std_' + each_metric] ** 2) / 2)
        
        grouped_data_benchmark_list.append(bm_data)
    
    return grouped_data_benchmark_list

def test_best_practice(
    data: pd.DataFrame,
    metrics: list,
    hrvar: list,
    bp: dict = {'Emails_sent': 10}
):
    """
    Takes in a DataFrame representing a Viva Insights person query and returns a list of DataFrames containing the results of the best practice test.
    
    The function adds the results of the t-test and the benchmark mean to the DataFrame for each metric.

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
        A list of DataFrames. Each DataFrame contains the results of the t-test for one metric. The DataFrame includes the original data, the benchmark mean, the p-value of the t-test, and a boolean column indicating whether the result is statistically significant at the 0.05 level.
    
    """
    
    #TODO: PERFORM CHECKS IF DICTIONARY VALUES DO NOT MATCH THOSE PROVIDED IN METRICS
    
    grouped_data_benchmark_list = []
    
    for each_metric in metrics:
        bm_data = vi.create_rank_calc(
            data,
            metric = each_metric,
            hrvar = hrvar,
            stats = True
        )
        
        # Filter by minimum group size
        bm_data = bm_data[bm_data['n'] >= 5]
        
        # Extract benchmark mean from dictionary
        bm_mean = bp[each_metric]
        
        # Attach benchmark mean to each row
        bm_data['benchmark_mean'] = bm_mean
        
        # Calculate percentage difference from benchmark mean
        bm_data['perc_diff'] = (bm_data['metric'] - bm_mean) / bm_mean * 100        
        
        grouped_data_benchmark_list.append(bm_data)
        
    return grouped_data_benchmark_list




#TODO: NOT COMPLETE
def create_inc_bm(
    data: pd.DataFrame,
    metric: str,
    hrvar: str,
    bm_data: pd.DataFrame = None,
    min_group: int = 5
):
    """    
    Calculates the number of employees who fall above, below, or equal to the population average for a given metric.

    If `bm_data` is provided, the population represented by this data frame will be used to calculate the population average. Otherwise, the population average is calculated from the `data` DataFrame.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the data to be analyzed. Each row represents an observation and each column represents a variable.

    metric : str
        The metric to be analyzed. This should correspond to a column name in `data`.

    hrvar : str
        The human resources variable to be used in the analysis. This should correspond to a column name in `data`.

    bm_data : pd.DataFrame, optional
        An optional DataFrame representing the population to be used for calculating the population average. If not provided, the population average is calculated from the `data` DataFrame.

    min_group : int, optional
        The minimum group size for the analysis. By default, the minimum group size is 5.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the results of the analysis. The DataFrame includes the original data, a new column indicating whether each observation is above, below, or equal to the population average, and the number of unique employees in each category for each group.

    Notes
    -----
    The function creates a copy of the `data` DataFrame to avoid modifying the original data. It then calculates the population average and the number of unique employees in the population. It adds a new column to the DataFrame indicating whether each observation is above, below, or equal to the population average. Finally, it groups the data by the `hrvar` and the new column, and calculates the number of unique employees in each category for each group.
    """
    
    # Population average
    if bm_data is not None:
        pop_mean = bm_data['pop_mean_' + metric]
        pop_n = bm_data['PersonId'].nunique()
    else:
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
    
    # Filter by minimum group size
    data_trans = data_trans[data_trans['n'] >= min_group]
    
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
    
    list_bp = test_best_practice(data = data, metrics = metrics, hrvar = hrvar, bp = {'Email_hours': 10})
    
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