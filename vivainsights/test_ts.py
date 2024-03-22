# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np
import re 
from vivainsights.create_int_bm import *

def test_ts(data: pd.DataFrame,
                  metrics: list,
                  hrvar: list = ["Organization", "SupervisorIndicator"],
                  min_group: int = 5,
                  bp: dict = {},
                  bm_hrvar: list = ["FunctionType", "SupervisorIndicator"],
                  return_type: str = 'full'):
    """
    This function takes in a DataFrame representing a Viva Insights person query and returns a list of DataFrames containing the results of the trend test.
    
    The function identifies the latest date in the data, and defines two periods: the last four weeks and the last twelve weeks. 
    
    It then initializes a list of exception metrics where lower values and downward trends are notable. 

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

    min_group : int, optional
        The minimum group size set for privacy. Defaults to 5.
        Groups with fewer people than `min_group` will not be included in the analysis.
        
    bp : dict
        A dictionary containing the benchmark mean for each metric and the directionality of the threshold.  
        `bp` requires a two-level nested dictionary where the first level consists of two explicit keys: 'above' and 'below'.
        Each of these keys maps to a second-level dictionary, which contains its own set of key-value pairs.
        The keys in the second-level dictionaries represent metrics, and the values represent the corresponding thresholds
        The keys should correspond to the metric names and the values should be the benchmark means. 
        
    bm_hrvar: list, optional
        A list variables to be used to create the benchmark for the like-for-like internal benchmark test. 
        By default, the variables are 'FunctionType' and 'SupervisorIndicator'.
        This list cannot be empty and must be of maximum length 2.
        
    return_type: str, optional
        The type of output to return. By default, the output is set to 'full'. Other options include 'consec_weeks', 'headlines', and 'plot'.

    Returns
    -------
    list
        A list of DataFrames. Each DataFrame contains the results of the trend test for one metric.
    """    
    
    # Count number of unique dates in `MetricDate`
    # If fewer than 12 unique values, return an error message
    if data['MetricDate'].nunique() < 12:
        print('Warning: fewer than 12 unique dates in `MetricDate`. Consider using a larger dataset for more accurate results.')
    
    # Message if fewer than 52 weeks of data available
    if data['MetricDate'].nunique() < 52:
        print('Note: using only ' + str(data['MetricDate'].nunique()) + ' weeks of data when calculating all time average')
    
    # If `bp` hasn't got a key for 'above', or 'below', create an empty key
    bp.setdefault('above', {})
    bp.setdefault('below', {})
    
    # set of unique metrics across 'above' and 'below'
    combined_keys = set(bp["above"].keys()) | set(bp["below"].keys())
    
    # If keys in key-value pairs in `bp` dictionary do not match those in `metrics`, return a warning message
    if combined_keys != set(metrics):
        print('Warning: keys in `bp` dictionary do not match those in `metrics`. Only matched metrics will be calculated.')  
    
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

    # Initialize empty lists for storing DataFrames
    grouped_data_list = []
    grouped_data_list_consec = []
    grouped_data_list_headlines = []
    
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
            
            # Check that MetricDate is datetime format, otherwise coerce to datetime
            if not pd.api.types.is_datetime64_any_dtype(grouped_data['MetricDate']):
                grouped_data['MetricDate'] = pd.to_datetime(grouped_data['MetricDate'])    
            
            # Order by MetricDate (ascending)
            grouped_data = grouped_data.sort_values(by = [each_hrvar, 'MetricDate'], ascending = True)            
                        
            # Calculate moving averages                                    
            grouped_data['4_Period_MA_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].transform(lambda x: x.rolling(window=4, min_periods=1).mean())
            grouped_data['12_Period_MA_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].transform(lambda x: x.rolling(window=12, min_periods=1).mean())
            grouped_data['All_Time_Avg_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].transform(lambda x: x.rolling(window=52, min_periods=1).mean())   
            grouped_data['Last_Week_4MA_' + each_metric] = grouped_data.groupby(each_hrvar)['4_Period_MA_' + each_metric].shift(1) # Previous week's 4MA
        
            # Calculate cumulative increases / decreases
            grouped_data['Diff_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].diff() # Difference between current and previous value
            grouped_data['SignDiff_' + each_metric] = np.sign(grouped_data['Diff_' + each_metric]) # Sign of the difference            
            grouped_data['SignChange_' + each_metric] = grouped_data.groupby(each_hrvar)['SignDiff_' + each_metric].transform(lambda x: x.ne(x.shift()).cumsum())
            grouped_data['CumIncrease_' + each_metric] = grouped_data.groupby([each_hrvar, 'SignChange_' + each_metric]).cumcount().where(grouped_data['SignDiff_' + each_metric] == 1, 0)
            grouped_data['CumDecrease_' + each_metric] = grouped_data.groupby([each_hrvar, 'SignChange_' + each_metric]).cumcount().where(grouped_data['SignDiff_' + each_metric] == -1, 0)   
        
            # Interest Test #1A: Does 4MA exceed threshold value? 
            if each_metric not in bp['above'].keys():
                grouped_data['Test1_4MA_Exceed_Threshold_' + each_metric] = False
            else:
                grouped_data['Test1_4MA_Exceed_Threshold_' + each_metric] = grouped_data['4_Period_MA_' + each_metric] > bp['above'][each_metric]
                
            # Interest Test #1B: Does 4MA fall below threshold value?
            if each_metric not in bp['below'].keys():
                grouped_data['Test1_4MA_Fall_Below_Threshold_' + each_metric] = False
            else:
                grouped_data['Test1_4MA_Fall_Below_Threshold_' + each_metric] = grouped_data['4_Period_MA_' + each_metric] < bp['below'][each_metric]     

            # Interest Test #2: does the 4MA exceed the 12MA, indicating that the metric is trending upwards?
            # 4MA flipping the 12MA
            grouped_data['Test2_4MA_Flipped_12MA_' + each_metric] = grouped_data.apply(
                lambda row: (row['4_Period_MA_' + each_metric] > row['12_Period_MA_' + each_metric] and 
                             row['Last_Week_4MA_' + each_metric] <= row['12_Period_MA_' + each_metric])
                if each_metric not in exception_metrics
                else (row['4_Period_MA_' + each_metric] < row['12_Period_MA_' + each_metric] and
                      row['Last_Week_4MA_' + each_metric] >= row['12_Period_MA_' + each_metric]), axis=1
            )

            # Stdev
            grouped_data['Stdev_' + each_metric] = grouped_data.groupby(each_hrvar)[each_metric].transform(lambda x: x.rolling(window=long_period, min_periods=1).std())

            # Group rank
            order = ranking_order[each_metric] == 'high'
            grouped_data['Rank_' + each_metric] = grouped_data.groupby('MetricDate')[each_metric].rank(ascending=not order)
            grouped_data['4_Week_Avg_Rank_' + each_metric] = grouped_data.groupby(each_hrvar)['Rank_' + each_metric].transform(lambda x: x.rolling(window=4, min_periods=1).mean())
            grouped_data['12_Week_Avg_Rank_' + each_metric] = grouped_data.groupby(each_hrvar)['Rank_' + each_metric].transform(lambda x: x.rolling(window=12, min_periods=1).mean())

            # Interest Test #3: Current value is closer to the 4MA than the 12MA
            grouped_data['Diff_Current_4MA' + each_metric] = abs(grouped_data[each_metric] - grouped_data['4_Period_MA_' + each_metric])
            grouped_data['Diff_Current_12MA' + each_metric] = abs(grouped_data[each_metric] - grouped_data['12_Period_MA_' + each_metric])
            grouped_data['Test3_Diff_Current_4MA_Over_12MA_' + each_metric] = grouped_data['Diff_Current_4MA' + each_metric] < grouped_data['Diff_Current_12MA' + each_metric]

            # Interest Test #4: Current value exceeds the 52 week average            
            grouped_data['Test4_Current_Exceed_52Wk_Avg_' + each_metric] = grouped_data[each_metric] > grouped_data['All_Time_Avg_' + each_metric]
            
            # Interest Test #5: Current value does not exceed the 4MA by >2 stdev (not a spike)
            grouped_data['Test5_Current_LessThan_4MA_2Stdev_' + each_metric] = (
                grouped_data[each_metric] < (grouped_data['4_Period_MA_' + each_metric] + 2 * grouped_data['Stdev_' + each_metric])
                )     
            
            # Interest Test #6: Current value against 4MA and 12MA
            dpc4ma_str = 'DiffP_Current_4MA' + each_metric # Percentage diff of current vs 4MA
            dcp12ma_str = 'DiffP_Current_12MA' + each_metric # Percentage diff of current vs 12MA          
            
            grouped_data[dpc4ma_str] = (grouped_data[each_metric] - grouped_data['4_Period_MA_' + each_metric]) / grouped_data['4_Period_MA_' + each_metric]
            grouped_data[dcp12ma_str] = (grouped_data[each_metric] - grouped_data['12_Period_MA_' + each_metric]) / grouped_data['12_Period_MA_' + each_metric]
            grouped_data['DiffP_Total'] = grouped_data[dpc4ma_str] + grouped_data[dcp12ma_str]
            grouped_data['Test6_DiffP_Total_IsLarge'] = (abs(grouped_data['DiffP_Total']) > 0.2)       
            
            # Interest Test #7: Cumulative increases and decreases            
            grouped_data['Test7_CumChange4Weeks_' + each_metric] = ((grouped_data['CumIncrease_' + each_metric] >= 3) | (grouped_data['CumDecrease_' + each_metric] >= 3))
            
            # Reorder columns
            cols = grouped_data.columns.tolist()
            test_cols = [col for col in cols if re.match(r'Test[0-9]_', col)]
            other_cols = [col for col in cols if not re.match(r'Test[0-9]_', col)]
            new_order_cols = other_cols + test_cols
            grouped_data = grouped_data[new_order_cols]
            
            # Calculate Interest Score from tests
            # Sum rowwise from all columns that start with 'Test_'
            grouped_data['Interest_Score'] = grouped_data[[col for col in grouped_data.columns if re.match(r'Test[0-9]_', col)]].sum(axis=1)
            
            # Bring in internal benchmark moving averages
            ts_int_bm_df = create_ts_int_bm_lfl(
                data = data,
                metric = each_metric,
                hrvar = each_hrvar,
                bm_hrvar = bm_hrvar
            )
            
            grouped_data = grouped_data.merge(ts_int_bm_df, on = ['MetricDate', each_hrvar], how = 'left')
            
            grouped_data_list.append(grouped_data)
            
            # Consecutive weeks ------------------------------------------------
            # Initialize empty list for storing consecutive weeks
            list_consec_weeks = []
            
            for each_group in groups:
                # Filter the DataFrame for the specific group
                each_df = grouped_data[grouped_data[each_hrvar] == each_group]
                # Sort the data by date in descending order
                each_df = each_df.sort_values('MetricDate', ascending = False)
                consecutive_weeks = 0
                for _, row in each_df.iterrows():
                    if row[f'Test2_4MA_Flipped_12MA_{each_metric}'] == True:
                        consecutive_weeks += 1
                    else:
                        break
                list_consec_weeks.append(consecutive_weeks)
            
            consec_weeks_df = pd.DataFrame({
                each_hrvar: groups,
                'Consecutive_Weeks': list_consec_weeks
            })
            
            grouped_data_list_consec.append(consec_weeks_df)
            
            # Headlines -------------------------------------------------------            
            # Filter by interesting headlines only
            grouped_data_headlines = grouped_data.loc[
                (grouped_data['Interest_Score'] >= 3) &
                (grouped_data['Test4_Current_Exceed_52Wk_Avg_' + each_metric] == True) &
                (grouped_data['Test2_4MA_Flipped_12MA_' + each_metric] == True)
            ].copy()
            
            # Ensure both must have the same sign
            grouped_data_headlines = grouped_data_headlines[
                grouped_data_headlines[dpc4ma_str] * 
                grouped_data_headlines[dcp12ma_str] > 0
            ]
            
            # Extract sign if identical
            grouped_data_headlines['TrendSign'] = np.where(
                np.sign(grouped_data_headlines[dpc4ma_str]) == np.sign(grouped_data_headlines[dcp12ma_str]),
                np.sign(grouped_data_headlines[dpc4ma_str]),
                np.nan
            )
                        
            # Filter by latest date only
            grouped_data_headlines = grouped_data_headlines[grouped_data_headlines['MetricDate'] == latest_date]
            
            # Generate headlines
            grouped_data_headlines['Headlines'] = (
                'For ' + each_hrvar + '==' + grouped_data_headlines[each_hrvar].astype(str) +
                ' (' + grouped_data_headlines['MetricDate'].astype(str) + '), ' +
                each_metric + ' (' + grouped_data_headlines[each_metric].round(1).astype(str) + ') is on ' +
                np.where(
                    grouped_data_headlines['TrendSign'] > 0,
                    'an upward trend, ',
                    'a downward trend, '
                ) +                 
                (grouped_data_headlines[dpc4ma_str] * 100).round(1).astype(str) + '%' +
                np.where(grouped_data_headlines[dpc4ma_str] >= 0, 
                        ' higher than its 4-week moving average ', 
                        ' lower than its 4-week moving average ') +
                '(' + grouped_data_headlines['4_Period_MA_' + each_metric].round(1).astype(str) + ') and ' +
                (grouped_data_headlines[dcp12ma_str] * 100).round(1).astype(str) + '%' +
                np.where(grouped_data_headlines[dcp12ma_str] >= 0,
                        ' higher than its 12-week moving average ',
                        ' lower than its 12-week moving average ') +
                '(' + grouped_data_headlines['12_Period_MA_' + each_metric].round(1).astype(str) + ').'
            ) + (
            # "For employees with similar [group1] and [group2], average metric (m) increased by about x%. "     
            "For employees with similar " + bm_hrvar[0] + " and " + bm_hrvar[1] + ", average " +
            each_metric + ' (' + grouped_data_headlines['InternalBenchmark_' + each_metric].round(1).astype(str) + ') ' +        
            np.where(grouped_data_headlines['PercDiffIntBench_12MA'] >= 0, 'increased', 'decreased') +
            " by about " +
            (grouped_data_headlines['PercDiffIntBench_12MA'] * 100).round(1).astype(str) +
            '% ' + 'against its 12-week moving average.'
            )
            
            # InterestScore - a min-max scaled score             
            min_score = grouped_data_headlines['Interest_Score'].min()
            max_score = grouped_data_headlines['Interest_Score'].max()

            if min_score == max_score:
                grouped_data_headlines['Interest_Score'] = 0
            else:
                grouped_data_headlines['Interest_Score'] = (grouped_data_headlines['Interest_Score'] - min_score) / (max_score - min_score)
            
            # Rank headlines by Interest Score
            grouped_data_headlines = grouped_data_headlines.sort_values(by='Interest_Score', ascending=False)
            
            # Add additional columns  
            grouped_data_headlines['TestType'] = 'Time Trend'
            grouped_data_headlines['Attribute'] = each_hrvar
            grouped_data_headlines['Metric'] = each_metric
            grouped_data_headlines = grouped_data_headlines.rename(
                columns={
                    each_hrvar: 'AttributeValue',
                    each_metric: 'MetricValue'}
                )
            
            # Clean up and reorder columns
            grouped_data_headlines = grouped_data_headlines[['TestType', 'Attribute', 'AttributeValue', 'Metric', 'MetricValue', 'n', 'Headlines', 'Interest_Score']]
            
            grouped_data_list_headlines.append(grouped_data_headlines)
            
            # Plot return -----------------------------------------------------
            
            if return_type == 'plot':
                
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
            
                        
    # Conditional for return type 
    if return_type == 'full': 
        
        for i in range(len(grouped_data_list)):
            # Filter by current week only
            grouped_data_list[i] = grouped_data_list[i][grouped_data_list[i]['MetricDate'] == max(grouped_data_list[i]['MetricDate'])]
        
        return grouped_data_list
            
    elif return_type == 'consec_weeks':

       return grouped_data_list_consec
                    
    elif return_type == 'headlines':
        
        if not grouped_data_list_headlines: # empty list
            
            return pd.DataFrame()  # return an empty DataFrame
        
        else:
        
            # Return row-bound DataFrame from list of headlines    
            headlines_df = pd.concat(grouped_data_list_headlines)
            
            # Sort 'Interest_Score' in descending order
            headlines_df = headlines_df.sort_values(by='Interest_Score', ascending=False)
            
            return headlines_df
    

def create_ts_int_bm_lfl(
    data: pd.DataFrame,
    metric: str,
    hrvar: str,
    bm_hrvar: list
):
    """
    Name 
    ----
    create_ts_int_bm_lfl
    
    Description
    ------------
    Creates time trend checks for the internal benchmark groups against its own longer term trends. 
    
    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the Person Query data to run the data on. 
    
    metric : str
        The metric in which the person-level and internal benchmark means will be calculated on. 
        
    hrvar : str
        The HR variable to group by.
        
    bm_hrvar : list
        The HR variables to group by for the internal benchmark. 
        Internally, this calls the `create_int_bm` function.
        
    Returns
    -------
    pd.DataFrame
        A grouped DataFrame in a group-week level, with the following metrics computed:
        - InternalBenchmark_{metric}
        - IntBench_4MA
        - IntBench_12MA
        - PercDiffIntBench_4MA
        - PercDiffIntBench_12MA       
    """
    
    # Get internal benchmark - return a grouped output
    df_int_bm = create_int_bm(
        data = data,
        metric = metric,
        hrvar = bm_hrvar, # takes a list
        level = 'group'
    )
    
    # Column names
    str_ibm_met = 'InternalBenchmark_' + metric
    
    # Narrow down to required columns
    # df_int_bm = df_int_bm[['MetricDate', str_ibm_met, 'IntBench_n']]
    
    # Check that MetricDate is datetime format, otherwise coerce to datetime
    if not pd.api.types.is_datetime64_any_dtype(df_int_bm['MetricDate']):
        df_int_bm['MetricDate'] = pd.to_datetime(df_int_bm['MetricDate'])    
    
    # Order by MetricDate (ascending)
    df_int_bm = df_int_bm.sort_values(by = 'MetricDate', ascending = True)  
    
    # Calculate moving averages for each group-combination                                    
    df_int_bm['IntBench_4MA'] = df_int_bm.groupby(bm_hrvar)[str_ibm_met].transform(lambda x: x.rolling(window=4, min_periods=1).mean())
    df_int_bm['IntBench_12MA'] = df_int_bm.groupby(bm_hrvar)[str_ibm_met].transform(lambda x: x.rolling(window=12, min_periods=1).mean())
    df_int_bm['IntBench_AllTimeMA'] = df_int_bm.groupby(bm_hrvar)[str_ibm_met].transform(lambda x: x.rolling(window=52, min_periods=1).mean())  
    
    # Get original benchmark groups
    group_columns = ['PersonId', 'MetricDate', metric] + bm_hrvar
    bm_group_df = data[group_columns].copy()
    
    # Join internal benchmark back to original data
    bm_group_df = bm_group_df.merge(df_int_bm, on = ['MetricDate'] + bm_hrvar, how = 'left')
    
    # Set of hrvar that exists in `bm_hrvar` but not `hrvar`
    diff_hrvar = list(set(bm_hrvar) - set([hrvar]))    
    
    # Narrow down to required columns
    bm_group_df = bm_group_df[['PersonId', 'MetricDate', str_ibm_met, 'IntBench_n' , 'IntBench_4MA', 'IntBench_12MA'] + diff_hrvar] 
    
    # Attach this back to group
    group_df = data[['PersonId', 'MetricDate', metric, hrvar]].copy()
    group_df = group_df.merge(bm_group_df, on = ['PersonId', 'MetricDate'], how = 'left')
    group_df = group_df.groupby(['MetricDate', hrvar]).agg({
        str_ibm_met : 'mean', # current value of internal benchmark
        'IntBench_4MA' : 'mean',
        'IntBench_12MA' : 'mean'
    })    
    
    # Difference between internal benchmark and their own moving averages
    group_df['PercDiffIntBench_4MA'] = (group_df[str_ibm_met] - group_df['IntBench_4MA']) / group_df['IntBench_4MA']
    group_df['PercDiffIntBench_12MA'] = (group_df[str_ibm_met] - group_df['IntBench_12MA']) / group_df['IntBench_12MA']
    
    return group_df
    