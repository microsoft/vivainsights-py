# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
from datetime import timedelta
import vivainsights as vi
from scipy import stats

def identify_nkw(
    data: pd.DataFrame,
    collab_threshold = 5,
    return_type = 'data_summary'
):
    """
    Identifies non-knowledge workers based on their average collaboration hours.

    This function groups the input data by 'PersonId' and 'Organization', calculates the mean collaboration hours for each group, and flags those with average collaboration hours below a specified threshold as non-knowledge workers. It then calculates the proportion of non-knowledge workers in each organization.

    Args:
        data (pd.DataFrame): The input data. Must contain the columns 'PersonId', 'Organization', and 'Collaboration_hours'.
        collab_threshold (int, optional): The threshold for average collaboration hours below which a person is considered a non-knowledge worker. Defaults to 5.
        return_type (str, optional): Specifies the type of data to return. 
        If 'data_with_flag', returns the input data with an additional 'flag_nkw' column indicating whether each person is a non-knowledge worker. 
        If 'data_summary', returns a summary of the number and proportion of non-knowledge workers in each organization. 
        If 'text', returns a text summary of the number and proportion of non-knowledge workers in each organization.
        Defaults to 'data_summary'.

    Returns:
        pd.DataFrame: The output data, as specified by the 'return_type' parameter.
    """
    summary_byPersonId = (
        data.groupby(['PersonId', 'Organization'])
        .agg(mean_collab=('Collaboration_hours', 'mean'))
        .reset_index()
    )
    
    summary_byPersonId['flag_nkw'] = ['kw' if x >= collab_threshold else 'nkw' for x in summary_byPersonId['mean_collab']]

    data_with_flag = pd.merge(data, summary_byPersonId[['PersonId', 'flag_nkw']], on='PersonId', how='left')    

    summary_byOrganization = (
        summary_byPersonId.groupby(['Organization', 'flag_nkw'])
        .size()
        .reset_index(name='total')
    )
    
    summary_byOrganization['perc'] = summary_byOrganization.groupby('Organization')['total'].apply(lambda x: x / x.sum()).reset_index(drop = True)
    summary_byOrganization = summary_byOrganization[summary_byOrganization['flag_nkw'] == 'nkw']
    summary_byOrganization = summary_byOrganization.rename(columns={'total': 'n_nkw', 'perc': 'perc_nkw'})
    summary_byOrganization = summary_byOrganization[['Organization', 'n_nkw', 'perc_nkw']]
 
    n_nkw = (summary_byPersonId['flag_nkw'] == 'nkw').sum()
 
    if n_nkw == 0:
        flagMessage = f"[Pass] There are no non-knowledge workers identified (average collaboration hours below {collab_threshold} hours)."
    else:
        flagMessage = f"[Warning] Out of a population of {data['PersonId'].nunique()}, there are {n_nkw} employees who may be non-knowledge workers (average collaboration hours below {collab_threshold} hours)."
 
    if return_type == "data_with_flag":
        return data_with_flag
    elif return_type == 'data_summary':
        return summary_byOrganization
    elif return_type == 'text':
        return flagMessage  
    elif return_type in ["data_clean", "data_cleaned"]:
        return data_with_flag[data_with_flag['flag_nkw'] == 'kw']
    else:
        print('Invalid value supplied to `return_type`')
