#--------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
from scipy.stats import mstats
from scipy.stats import cumfreq
from itertools import groupby

def calculate_IV(data, outcome, predictor, bins):
    pred_var = data[predictor]
    outc_var = data[outcome]

    # Check inputs
    if outc_var.isna().sum() > 0:
        raise ValueError(f"dependent variable {outcome} has missing values in the input training data frame")

    # Compute q
    q = mstats.mquantiles(pred_var, prob=np.arange(1, bins) / bins, alphap=0, betap=0)

    # Compute cuts
    cuts = np.unique(q)

    # Compute intervals
    intervals = np.digitize(pred_var, bins=cuts, right=False)

    # Compute cut_table
    cut_table = pd.crosstab(intervals, outc_var).reset_index()

    # get min/max
    cut_table_2 = pd.DataFrame({
        'var': pred_var,
        'intervals': intervals
    }).groupby('intervals').agg(
        min=('var', 'min'),
        max=('var', 'max'),
        n=('var', 'size')
    ).reset_index().round({'min': 1, 'max': 1})
    
    cut_table_2[predictor] = cut_table_2.apply(lambda row: f"[{row['min']},{row['max']}]", axis=1)
    cut_table_2['percentage'] = cut_table_2['n'] / cut_table_2['n'].sum()
    cut_table_2 = cut_table_2[[predictor, 'intervals', 'n', 'percentage']]

    # Create variables that are double
    cut_table_1 = cut_table[1].values.astype(float)
    cut_table_0 = cut_table[0].values.astype(float)

    # Non-events in group
    n_non_event = cut_table_1 * np.sum(cut_table_0)
    n_yes_event = cut_table_0 * np.sum(cut_table_1)

    # Compute WOE
    cut_table_2['WOE'] = np.where((cut_table[1] > 0) & (cut_table[0] > 0), np.log(n_non_event / n_yes_event), 0)

    # Compute IV_weight
    p1 = cut_table[1] / cut_table[1].sum()
    p0 = cut_table[0] / cut_table[0].sum()

    cut_table_2['IV_weight'] = p1 - p0
    cut_table_2['IV'] = cut_table_2['WOE'] * cut_table_2['IV_weight']

    cut_table_2['IV'] = cut_table_2['IV'].cumsum()

    return cut_table_2[[predictor, 'n', 'percentage', 'WOE', 'IV']]

def map_IV(data, outcome, predictors=None, bins=5):
    if predictors is None:
        predictors = data.select_dtypes(include='number').columns.difference([outcome])

    # List of individual tables
    Tables = {pred: calculate_IV(data, outcome, pred, bins) for pred in predictors}

    # Compile Summary Table
    Summary = pd.DataFrame({'Variable': list(Tables.keys())}).assign(
        IV=lambda df: df['Variable'].map(lambda var: Tables[var].iloc[-1]['IV'])
    ).sort_values(by='IV', ascending=False)
    # print({'Tables': Tables, 'Summary': Summary})
    return {'Tables': Tables, 'Summary': Summary}