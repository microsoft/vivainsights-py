# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd

def create_int_bm(
    data: pd.DataFrame,
    metric: str,
    hrvar: list = ['Organization', 'SupervisorIndicator']
    ):
    """
    Compare a metric mean for each employee against the internal benchmark of like-for-like employees, using group combinations from two or more HR variables. 

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the Person Query data to run the data on. 
    
    metric : str
        The metric in which the person-level and internal benchmark means will be calculated on. 

    hrvar : list
        The HR variables to group by. Defaults to ['Organization', 'SupervisorIndicator'].

    Returns
    ----------
    output : pd.DataFrame
        A person-level DataFrame with the original person-level means and the internal benchmark mean of the selected metric.
        
    Example
    -------    
    >>> create_int_bm(
    data = vi.load_pq_data(),
    metric = 'Emails_sent',
    hrvar = ['Organization', 'SupervisorIndicator']
    )
    """
    
    
    # Calculate the mean of a selected metric, grouped by two or more HR variable ----------------
    group_columns = ['PersonId', 'MetricDate', metric] + hrvar
    
    # A copy of the original data, with required columns only
    grouped_df = data[group_columns]
    
    # Calculate internal benchmarks by date snapshot and HR attributes
    int_bm_df = data.groupby(['MetricDate'] + hrvar).agg(
        metric = (metric, 'mean'),
        IntBench_n = ('PersonId', 'nunique'),
        IntBench_sd = (metric, 'std')
        ).reset_index()
    
    int_bm_df.rename(columns = {'metric': 'InternalBenchmark_' + metric}, inplace = True)    
    
    # Join internal benchmark back to grouped_df     
    grouped_df = grouped_df.merge(int_bm_df, on = ['MetricDate'] + hrvar, how = 'left')   
    
    # Calculate differences
    grouped_df.rename(columns = {'metric' : metric}, inplace = True)
    grouped_df['DiffIntBench_' + metric] = grouped_df[metric] - grouped_df['InternalBenchmark_' + metric]
    grouped_df['PercDiffIntBench_' + metric] = grouped_df['DiffIntBench_' + metric] / grouped_df['InternalBenchmark_' + metric]
    
    # Return output    
    return grouped_df