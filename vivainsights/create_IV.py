# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
The code defines a function `create_IV` that calculates and visualizes the mean of a selected
Specify an outcome variable and return IV outputs.

The metrics are first aggregated at a user-level prior to being aggregated at the level of the HR variable. The function `create_bar` returns either a plot object or a table, depending on the value passed to `return_type`.

return String specifying what to return. This must be one of the
following strings:
- "plot"
- "summary"
- "list"
- "plot-WOE"
- "IV"

"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import wilcoxon
from scipy.stats import mstats
import math
import warnings


# Ignore warnings for cleaner output
warnings.filterwarnings("ignore")


def p_test(data, outcome, behavior, paired=False):
    """
    Performs Wilcoxon signed-rank test or rank-sum test between two groups.

    Parameters:
    - data: DataFrame containing the data
    - outcome: Name of the outcome variable
    - behavior: List of behavior variables to test
    - paired: Boolean indicating if the test should be paired or not

    Returns:
    - DataFrame with variables and corresponding p-values
    
    """
    
    # Filter the dataset based on the outcome variable
    train = data[data[outcome].isin([0, 1])].copy()

    # Convert outcome to string and then to a factor
    train[outcome] = train[outcome].astype(str).astype('category')
    p_value_dict = {}
    for i in behavior:
        # Separate data into positive and negative outcomes
        pos = train[train[outcome] == '1'][i].dropna()
        neg = train[train[outcome] == '0'][i].dropna()

        # Ensure that the lengths of pos and neg are the same
        min_len = min(len(pos), len(neg))
        pos = pos[:min_len]
        neg = neg[:min_len]

        # Perform Wilcoxon signed-rank test (or rank-sum test for unpaired data)
        _, p_value = wilcoxon(pos, neg) if paired else wilcoxon(pos, neg, alternative='two-sided')
        p_value_dict.update({i: p_value})

    data_frame = pd.DataFrame(list(p_value_dict.items()), columns=['Variable', 'pval'])

    return data_frame


def calculate_IV(data, outcome, predictor, bins):
    """
    Calculates Information Value (IV) for a predictor variable.

    Parameters:
    - data: DataFrame containing the data
    - outcome: Name of the outcome variable
    - predictor: Name of the predictor variable
    - bins: Number of bins for binning the predictor variable

    Returns:
    - DataFrame with IV calculations for the predictor variable
    """
    
    pred_var = data[predictor]
    outc_var = data[outcome]

    # Check inputs
    if outc_var.isna().sum() > 0:
        raise ValueError(f"dependent variable {outcome} has missing values in the input training data frame")

    # Compute quantiles
    q = mstats.mquantiles(pred_var, prob=np.arange(1, bins) / bins, alphap=0, betap=0)

    # Compute cuts
    cuts = np.unique(q)

    # Compute intervals
    intervals = np.digitize(pred_var, bins=cuts, right=False)

    # Compute cut_table
    cut_table = pd.crosstab(intervals, outc_var).reset_index()

    # Compute min/max and percentage
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

    # Calculate Non-events and Events
    cut_table_1 = cut_table[1].values.astype(float)
    cut_table_0 = cut_table[0].values.astype(float)
    n_non_event = cut_table_1 * np.sum(cut_table_0)
    n_yes_event = cut_table_0 * np.sum(cut_table_1)

    # Compute WOE (Weight of Evidence)
    cut_table_2['WOE'] = np.where((cut_table[1] > 0) & (cut_table[0] > 0), np.log(n_non_event / n_yes_event), 0)

    # Compute IV_weight
    p1 = cut_table[1] / cut_table[1].sum()
    p0 = cut_table[0] / cut_table[0].sum()
    cut_table_2['IV_weight'] = p1 - p0
    cut_table_2['IV'] = cut_table_2['WOE'] * cut_table_2['IV_weight']
    cut_table_2['IV'] = cut_table_2['IV'].cumsum()

    return cut_table_2[[predictor, 'n', 'percentage', 'WOE', 'IV']]


def map_IV(data, outcome, predictors=None, bins=5):
    """
    Maps Information Value (IV) calculations for multiple predictor variables.

    Parameters:
    - data: DataFrame containing the data
    - outcome: Name of the outcome variable
    - predictors: List of predictor variables (if None, all numeric variables except outcome are used)
    - bins: Number of bins for binning the predictor variables

    Returns:
    - Dictionary containing IV calculations for each predictor variable and a summary DataFrame    
    """
    
    if predictors is None:
        predictors = data.select_dtypes(include='number').columns.difference([outcome])

    # List of individual tables
    Tables = {pred: calculate_IV(data, outcome, pred, bins) for pred in predictors}

    # Compile Summary Table
    Summary = pd.DataFrame({'Variable': list(Tables.keys())}).assign(
        IV=lambda df: df['Variable'].map(lambda var: Tables[var].iloc[-1]['IV'])
    ).sort_values(by='IV', ascending=False)
    return {'Tables': Tables, 'Summary': Summary}


def plot_WOE(IV, predictor):
    """
    Plots Weight of Evidence (WOE) for a predictor variable.

    Parameters:
    - IV: Dictionary containing IV calculations for each predictor variable
    - predictor: Name of the predictor variable

    Returns:
    - None (plots the WOE)    
    """
    
    # Identify right table
    plot_table = IV['Tables'][predictor]
    
    # Get range
    WOE_values = [table['WOE'] for table in IV['Tables'].values()]
    for i in range(0,len(WOE_values)):
        WOE_range = np.min(WOE_values[i]), np.max(WOE_values[i])
    mn=math.floor(np.min(plot_table['WOE']))
    mx=math.ceil(np.max(plot_table['WOE']))
    tick_lst=list(range(mn,mx+1))
    
    # Plot
    plt.figure(figsize=(12, 8))
    sns.barplot(x=predictor, y='WOE', data=plot_table, color='#8BC7E0')
    for index, value in enumerate(plot_table['WOE']):
        plt.text(index, value, round(value, 1), ha='right', va='top' if value < 0 else 'bottom',color='red' if value < 0 else 'green')
    plt.title(predictor)
    plt.xlabel(predictor)
    plt.ylabel("Weight of Evidence (WOE)")
    plt.ylim(WOE_range[0] * 1.1, WOE_range[1] * 1.1)
    plt.yticks(tick_lst) 
    plt.show()


def create_IV(data, predictors=None, outcome=None, bins=5, siglevel=0.05, exc_sig=False, return_type="plot"):
    """
    Creates Information Value (IV) analysis for predictor variables.

    Parameters:
    -----------
    - data: DataFrame containing the data
    - predictors: List of predictor variables
    - outcome: Name of the outcome variable
    - bins: Number of bins for binning the predictor variables
    - siglevel: Significance level
    - exc_sig: Boolean indicating if non-significant predictors should be excluded
    - return_type: Type of output to return ("plot", "summary", "list", "plot-WOE", "IV")

    Returns:
    --------
    _type_
        the type of output to return. Defaults to "plot".
        the type of output to return. "summary".
        the type of output to return. "list".
        the type of output to return. "plot-WOE".
        the type of output to return. "IV".
    
    Note    
    ----
    >>> create_IV function return_type 'list' and 'summary' has output format as a dictionary, kindly use for loop to access the key and values.
    >>> create_IV function return_type 'IV' has output format as a tuple, tuple element 'output_list'format is dictionary hence kindly use for loop to access the key and values.

    Example
    -------
    >>> import numpy as np

    >>> 1. df["X"] = np.where(df["Internal_network_size"] > 40, 1, 0)
    >>>    result = create_IV(df, predictors=["Email_hours",
    >>>                            "Meeting_hours",
    >>>                            "Chat_hours"
    >>>                         ], outcome="X",exc_sig=False, return_type="IV")

    >>> 2. df["X"] = np.where(df["Internal_network_size"] > 40, 1, 0)
    >>>   result = create_IV(df, predictors=["Email_hours",
    >>>                            "Meeting_hours",
    >>>                            "Chat_hours"
    >>>                         ], outcome="X",exc_sig=False, return_type="summary")

    >>> 3. df["X"] = np.where(df["Internal_network_size"] > 40, 1, 0)
    >>>   result = create_IV(df, predictors=["Email_hours",
    >>>                            "Meeting_hours",
    >>>                            "Chat_hours"
    >>>                         ], outcome="X",exc_sig=False, return_type="plot")    
    """
    
    # Preserve string
    pred_chr = predictors.copy() if predictors else None

    # Select training dataset
    if predictors is None:
        train = data.select_dtypes(include=np.number).dropna()
    else:
        train = data[predictors + [outcome]].dropna()

    # Calculate odds
    odds = train[outcome].sum() / (len(train[outcome]) - train[outcome].sum())
    lnodds = np.log(odds)

    # Assert
    if not isinstance(exc_sig, bool):
        raise ValueError("Invalid input to `exc_sig`")

    # Prepare predictors DataFrame
    predictors = pd.DataFrame({'Variable': np.array(train.columns)})
    predictors = predictors[predictors['Variable'] != outcome].reset_index(drop=True)
    predictors['Variable'] = predictors['Variable'].astype(str)

    # Perform statistical test and filter significant predictors
    predictors_pval = p_test(data=train, outcome=outcome, behavior=predictors["Variable"].tolist())
    predictors_pval = predictors_pval[predictors_pval["pval"] <= siglevel]

    if predictors_pval.shape[0] == 0:
        raise ValueError("No predictors where the p-value lies below the significance level.")

    train = train[predictors_pval["Variable"].tolist() + [outcome]]

    # IV Analysis
    IV = map_IV(train, outcome, bins=bins, predictors=predictors_pval["Variable"].tolist())
    IV_names = list(IV["Tables"].keys())
    IV_summary = pd.merge(IV["Summary"], predictors_pval, on="Variable")
    IV_summary["pval"] = IV_summary["pval"].round(10)

    # Output loop
    if return_type == "summary":
        print(IV_summary)
        return IV_summary

    elif return_type == "IV":
        output_list = {variable: IV["Tables"][variable].assign(
            ODDS=lambda df: np.exp(df["WOE"] + lnodds),
            PROB=lambda df: df["ODDS"] / (df["ODDS"] + 1)) for variable in IV_names}
        for key, df in output_list.items():
            print(f" {key} :\n",f"{df}\n")
        print(f"Summary : \n {IV_summary}\n")
        print(f"lnodds:{lnodds}")
        return output_list, IV_summary, lnodds

    elif return_type == "plot":
        top_n = min(12, IV_summary.shape[0])
        create_bar_asis(IV_summary,
                        group_var="Variable",
                        bar_var="IV",
                        title="Information Value (IV)",
                        subtitle=("Showing top", top_n, "predictors"),
                        caption=None,
                        ylab=None,
                        xlab=None,
                        percent=False,
                        bar_colour="default",
                        rounding=1)

    elif return_type == "plot-WOE":
        return [plot_WOE(IV, variable) for variable in IV["Summary"]["Variable"]]

    elif return_type == "list":
        output_list = {variable: IV["Tables"][variable].assign(
            ODDS=lambda df: np.exp(df["WOE"] + lnodds),
            PROB=lambda df: df["ODDS"] / (df["ODDS"] + 1)) for variable in IV_names}
        for key, df in output_list.items():
            print(f" {key}\n",f"Shape of the data: {df.shape}\n",f"data:\n{df}\n")
        return output_list
    else:
        raise ValueError("Please enter a valid input for `return_type`.")