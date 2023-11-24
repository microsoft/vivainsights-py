import pandas as pd
import numpy as np
from scipy.stats import mstats
from scipy.stats import chi2_contingency
from typing import List, Union

def calculate_IV(data, outcome, predictor, bins):
    pred_var = data[predictor]
    outc_var = data[outcome]

    # Check inputs
    if outc_var.isna().sum() > 0:
        raise ValueError(f"dependent variable {outcome} has missing values in the input training data frame")

    # Compute q
    q = mstats.mquantiles(pred_var, prob=np.arange(1, bins) / bins, alphap=0.5, betap=0.5)

    # Compute cuts
    cuts = np.unique(q)

    # Compute intervals
    intervals = np.digitize(pred_var, bins=cuts)

    # Compute cut_table
    cut_table = pd.crosstab(intervals, outc_var)

    # get min/max
    cut_table_2 = pd.DataFrame({
        'var': pred_var,
        'intervals': intervals
    }).groupby('intervals').agg({
        'var': ['min', 'max', 'count']
    }).reset_index()
    cut_table_2.columns = ['intervals', 'min', 'max', 'n']
    cut_table_2[predictor] = cut_table_2.apply(lambda row: f"[{round(row['min'], 1)},{round(row['max'], 1)}]", axis=1)
    cut_table_2['percentage'] = cut_table_2['n'] / cut_table_2['n'].sum()

    # Create variables that are double
    cut_table_1 = cut_table[1].values
    cut_table_0 = cut_table[0].values

    # Non-events in group
    n_non_event = cut_table_1 * cut_table_0.sum() # t$y_1*sum_y_0
    n_yes_event = cut_table_0 * cut_table_1.sum() # t$y_0*sum_y_1

    # Compute WOE
    cut_table_2['WOE'] = np.where((cut_table_1 > 0) & (cut_table_0 > 0), np.log(n_non_event / n_yes_event), 0)

    # Compute IV_weight
    p1 = cut_table_1 / cut_table_1.sum()
    p0 = cut_table_0 / cut_table_0.sum()

    cut_table_2['IV_weight'] = p1 - p0
    cut_table_2['IV'] = cut_table_2['WOE'] * cut_table_2['IV_weight']

    cut_table_2['IV'] = cut_table_2['IV'].cumsum()

    return cut_table_2[[predictor, 'n', 'percentage', 'WOE', 'IV']].rename(columns={'n': 'N', 'percentage': 'Percent'})


def map_IV(data: pd.DataFrame, outcome: str, predictors: Union[List[str], None] = None, bins: int = 10):
    if predictors is None:
        predictors = data.select_dtypes(include=[np.number]).columns.tolist()
        predictors.remove(outcome)

    tables = {}
    for pred in predictors:
        tables[pred] = calculate_IV(data, outcome, pred, bins)

    return tables




def create_IV(data: pd.DataFrame,
              outcome: str,
              predictors: Union[List[str], None] = None,
              bins: int = 5,
              siglevel: float = 0.05,
              exc_sig: bool = False,
              return_type: str = "plot"):
    # Preserve string
    pred_chr = predictors

    # Select training dataset
    if predictors is None:
        train = data.select_dtypes(include=[np.number]).dropna()
    else:
        train = data[predictors + [outcome]].dropna()

    # Calculate odds
    odds = train[outcome].sum() / (len(train[outcome]) - train[outcome].sum())
    lnodds = np.log(odds)

    # Assert
    if not isinstance(exc_sig, bool):
        raise ValueError("invalid input to `exc_sig`")

    # Calculate p-value
    predictors = [col for col in train.columns if col != outcome]

    if exc_sig:
        p_values = []
        for predictor in predictors:
            contingency_table = pd.crosstab(train[predictor], train[outcome])
            _, p_value, _, _ = chi2_contingency(contingency_table)
            p_values.append(p_value)

        predictors = [predictor for predictor, p_value in zip(predictors, p_values) if p_value <= siglevel]
        if len(predictors) == 0:
            raise ValueError("There are no predictors where the p-value lies below the significance level. You may set `exc_sig == False` or increase the threshold on `siglevel`.")

    train = train[predictors + [outcome]]

    # IV Analysis
    IV = map_IV(data=train, predictors=predictors, outcome=outcome, bins=bins)
    IV_names = list(IV.keys())

    # Implement your own IV_summary and handle_output functions here
    IV_summary = calculate_IV_summary(IV, predictors)
    return handle_output(return_type, IV, IV_summary, IV_names, lnodds)