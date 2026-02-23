# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Identify non-knowledge workers based on collaboration activity thresholds.
"""

__all__ = ['identify_nkw']

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
    """Identify non-knowledge workers based on collaboration activity.

    Groups the data by ``PersonId`` and ``Organization``, computes mean
    collaboration hours, and flags employees below the threshold as
    non-knowledge workers.

    Parameters
    ----------
    data : pandas.DataFrame
        Person query data.  Must contain ``PersonId``, ``Organization``,
        and ``Collaboration_hours``.
    collab_threshold : int, default 5
        Average weekly collaboration hours below which a person is
        considered a non-knowledge worker.
    return_type : str, default "data_summary"
        ``"data_with_flag"`` adds a ``flag_nkw`` column, ``"data_summary"``
        returns per-organization counts, ``"text"`` returns a diagnostic
        message, ``"data_clean"`` / ``"data_cleaned"`` returns only
        knowledge workers.

    Returns
    -------
    pandas.DataFrame or str
        Depending on *return_type*.

    Examples
    --------
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> vi.identify_nkw(pq_data, collab_threshold=15, return_type="text")
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
