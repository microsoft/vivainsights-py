import pandas as pd

def create_int_bm(
    data: pd.DataFrame,
    metric: str,
    hrvar: list = ['Organization', 'SupervisorIndicator'],
    mingroup: int = 5
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

    mingroup : int
        The minimum group size. Defaults to 5.

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
    group_columns = ['PersonId'] + hrvar    
    grouped_df = data.groupby(group_columns)[metric].mean().reset_index()
    
    int_bm_df = data.groupby(hrvar).agg(
        metric = (metric, 'mean'),
        n = ('PersonId', 'nunique')
        )
    int_bm_df = int_bm_df[int_bm_df['n'] >= mingroup]
    int_bm_df = int_bm_df.rename_axis(hrvar).reset_index()
    int_bm_df = int_bm_df.sort_values(by = 'metric', ascending=False)
    int_bm_df.rename(columns = {'metric': 'InternalBenchmark_' + metric}, inplace = True)    
    
    # Drop the n column from int_bm_df 
    int_bm_df = int_bm_df.drop(columns = 'n')
    
    # Join internal benchmark back to grouped_df     
    grouped_df = grouped_df.merge(int_bm_df, on = hrvar, how = 'left')   
    
    # Calculate differences
    grouped_df['DiffIntBench_' + metric] = grouped_df[metric] - grouped_df['InternalBenchmark_' + metric]
    grouped_df['PercDiffIntBench_' + metric] = grouped_df['DiffIntBench_' + metric] / grouped_df['InternalBenchmark_' + metric]
    
    # Return output    
    return grouped_df