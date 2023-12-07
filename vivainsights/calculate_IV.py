# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import pandas as pd
import numpy as np

def calculate_IV(data, outcome, predictor, bins):
    pred_var = data[predictor]
    outc_var = data[outcome]

    if outc_var.isna().sum() > 0:
        raise ValueError(f"dependent variable {outcome} has missing values in the input training data frame")

    q = np.percentile(pred_var, np.arange(1, bins) / bins * 100, interpolation='lower')
    cuts = np.unique(q)
    intervals = np.digitize(pred_var, cuts, right=False)

    cut_table = pd.crosstab(intervals, outc_var)
    cut_table_2 = pd.DataFrame({
        'var': pred_var,
        'intervals': intervals
    }).groupby('intervals').agg(
        min=('var', lambda x: round(x.min(), 1)),
        max=('var', lambda x: round(x.max(), 1)),
        n=('var', 'count')
    ).reset_index()
    cut_table_2[predictor] = cut_table_2.apply(lambda row: f"[{row['min']},{row['max']}]", axis=1)
    cut_table_2['percentage'] = cut_table_2['n'] / cut_table_2['n'].sum()

    cut_table_1 = cut_table[1].to_numpy(dtype=float)
    cut_table_0 = cut_table[0].to_numpy(dtype=float)
    n_non_event = cut_table_1 * cut_table_0.sum()
    n_yes_event = cut_table_0 * cut_table_1.sum()

    cut_table_2['WOE'] = np.where((cut_table[1] > 0) & (cut_table[0] > 0), np.log(n_non_event / n_yes_event), 0)

    p1 = cut_table[1] / cut_table[1].sum()
    p0 = cut_table[0] / cut_table[0].sum()
    cut_table_2['IV_weight'] = p1 - p0
    cut_table_2['IV'] = cut_table_2['WOE'] * cut_table_2['IV_weight']
    cut_table_2['IV'] = cut_table_2['IV'].cumsum()

    return cut_table_2[[predictor, 'intervals', 'n', 'percentage', 'WOE', 'IV']]

def map_IV(data, outcome, predictors=None, bins=10):
    if predictors is None:
        predictors = data.select_dtypes(include='number').columns.tolist()

    Tables = {}
    for pred in predictors:
        Tables[pred] = calculate_IV(data, outcome, pred, bins)

    Summary = pd.DataFrame({
        'Variable': list(Tables.keys()),
        'IV': [table['IV'].iloc[-1] for table in Tables.values()]
    }).sort_values(by='IV', ascending=False)

    return {'Tables': Tables, 'Summary': Summary}
