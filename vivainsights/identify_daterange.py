# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Takes a vector of dates and identify whether the frequency is 'daily', 'weekly', or 'monthly'. 
The primary use case for this function is to provide an accurate description of the query type 
used and for raising errors should a wrong date grouping be used in the data input.
"""
import pandas as pd

def identify_datefreq(x):
    x = pd.to_datetime(x)
    
    # Data frame for checking
    date_df = pd.DataFrame({
        "weekdays": pd.Series(list(pd.Series(x).dt.weekday.unique())),
        "n": pd.Series(list(pd.Series(x).dt.weekday.value_counts()))
    })
    
    if len(pd.Series(x).dt.month_name().unique()) == len(x):
        return "monthly"
    elif sum(date_df.loc[date_df.weekdays == 6].n) == len(x): # Check number of Sundays - should equal number of weeks if weekly
        return "weekly"
    elif len(date_df) >= 3: # At least 3 days of the week must be present
        return "daily"
    else:
        return "Unable to identify date frequency."

