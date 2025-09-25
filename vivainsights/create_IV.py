# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import wilcoxon
from scipy.stats import mstats
import math
import warnings
from vivainsights.create_bar_asis import *


# Ignore warnings for cleaner output
warnings.filterwarnings("ignore")


def p_test(
    data: pd.DataFrame,
    outcome: str,
    behavior: list,
    paired = False
    ):
    """
    Name
    -----
    p_test
    
    Description
    -----------
    Performs Wilcoxon signed-rank test or rank-sum test between two groups.

    Parameters
    ----------
    data : pd.DataFrame
        A Pandas DataFrame.
    outcome : str
        Name of the outcome variable.
    behavior : list
        List of behavior variables to test.
    paired : bool, optional
        Boolean indicating if the test should be paired or not. Default is False.

    Returns
    -------
    pd.DataFrame
        A DataFrame with variables and corresponding p-values.
    
    Examples
    --------    
    >>> import vivainsights as vi
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'outcome': [1, 0, 1, 0, 1],
    ...     'behavior1': [10, 20, 30, 40, 50],
    ...     'behavior2': [5, 15, 25, 35, 45]
    ... })
    >>> outcome = 'outcome'
    >>> behavior = ['behavior1', 'behavior2']
    >>> vi.p_test(data, outcome, behavior)
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


def calculate_IV(
    data: pd.DataFrame,
    outcome: str,
    predictor: str,
    bins: int
    ):
    """
    Name
    ----
    calculate_IV

    Description
    -----------
    Calculates Information Value (IV) between a single predictor variable and the outcome variable.

    Parameters
    ----------
    data : pd.DataFrame
        A DataFrame containing the data.
    outcome : str
        Name of the outcome variable.
    predictor : str
        Name of the predictor variable.
    bins : int
        Number of bins for binning the predictor variable.

    Returns
    -------
    pd.DataFrame
        A DataFrame with IV calculations for the predictor variable.

    Raises
    ------
    ValueError
        If the outcome variable has missing values in the input training data frame.

    Examples
    --------
    >>> import vivainsights as vi
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'outcome': [1, 0, 1, 0, 1],
    ...     'predictor': [10, 20, 30, 40, 50]
    ... })
    >>> outcome = 'outcome'
    >>> predictor = 'predictor'
    >>> bins = 5
    >>> vi.calculate_IV(data, outcome, predictor, bins)
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


def map_IV(
    data: pd.DataFrame,
    outcome: str,
    predictors = None,
    bins: int = 5
    ):
    """
    Name
    ----
    map_IV
    
    Description
    -----------
    Maps Information Value (IV) calculations for multiple predictor variables. 
    Calls `calculate_IV()` for every predictor-outcome variable pair.

    Parameters
    ----------
    - data: DataFrame containing the data
    - outcome: Name of the outcome variable
    - predictors: List of predictor variables (if None, all numeric variables except outcome are used)
    - bins: Number of bins for binning the predictor variables

    Returns
    -------
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


def plot_WOE(IV, predictor, figsize: tuple = None):
    """
    Name
    ----
    plot_WOE

    Description
    -----------
    Plots Weight of Evidence (WOE) for a predictor variable.

    Parameters
    ----------
    IV : dict
        Dictionary containing IV calculations for each predictor variable.
    predictor : str
        Name of the predictor variable.
    figsize : tuple, optional
        The `figsize` parameter is an optional tuple that specifies the size of the figure for the WOE plot visualization.
        It should be in the format `(width, height)`, where `width` and `height` are in inches. If not provided, a default size of (8, 6) will be used.

    Returns
    -------
    None
        This function doesn't return a value; it plots the WOE.

    Examples
    --------
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'outcome': [1, 0, 1, 0, 1],
    ...     'predictor': [10, 20, 30, 40, 50]
    ... })
    >>> outcome = 'outcome'
    >>> predictor = 'predictor'
    >>> bins = 5
    >>> IV = map_IV(data, outcome, [predictor], bins)
    >>> plot_WOE(IV, predictor)
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
    plt.figure(figsize=figsize if figsize else (8, 6))
    sns.barplot(x=predictor, y='WOE', data=plot_table, color='#8BC7E0')
    for index, value in enumerate(plot_table['WOE']):
        plt.text(index, value, round(value, 1), ha='right', va='top' if value < 0 else 'bottom',color='red' if value < 0 else 'green')
    plt.title(predictor)
    plt.xlabel(predictor)
    plt.ylabel("Weight of Evidence (WOE)")
    plt.ylim(WOE_range[0] * 1.1, WOE_range[1] * 1.1)
    plt.yticks(tick_lst) 
    plt.show()


def create_IV(
    data = pd.DataFrame,
    predictors = None,
    outcome:str = None,
    bins: int = 5,
    siglevel = 0.05,
    exc_sig: bool = False,
    return_type ="plot"
    ):
    """
    Name
    ----
    create_IV

    Description
    -----------
    Creates Information Value (IV) analysis for predictor variables.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the data.
    predictors : list, optional
        List of predictor variables.
    outcome : str
        Name of the outcome variable.
    bins : int, optional
        Number of bins for binning the predictor variables. Defaults to 5.
    siglevel : float, optional
        Significance level. Defaults to 0.05.
    exc_sig : bool, optional
        Boolean indicating if non-significant predictors should be excluded. 
        If True, only predictors with p-value <= siglevel are included in the analysis.
        If False, all predictors are included regardless of significance. Defaults to False.
    return_type : str, optional
        Type of output to return ("plot", "summary", "list", "plot-WOE", "IV"). Defaults to "plot".

    Returns
    -------
    Various
        The type of output to return. Can be "plot", "summary", "list", "plot-WOE", or "IV".
    
    Note    
    ----
      * create_IV function return_type 'list' and 'summary' has output format as a dictionary, please use for loop to access the key and values.
      * create_IV function return_type 'IV' has output format as a tuple, tuple element 'output_list'format is dictionary hence please use for loop to access the key and values.

    Example
    -------
    >>> import numpy as np
    >>> import vivainsights as vi
    >>> pq_data = vi.load_pq_data()
    >>> pred_vars = ["Email_hours", "Meeting_hours", "Chat_hours"]
    >>> pq_data["outcome_sim"] = np.where(pq_data["Internal_network_size"] > 40, 1, 0)

    >>> # Example 1: Return IV tables for all predictors without excluding non-significant ones
    >>> vi.create_IV(pq_data, predictors=pred_vars, outcome="outcome_sim", exc_sig=False, return_type="IV")

    >>> # Example 2: Exclude non-significant predictors and return summary
    >>> vi.create_IV(pq_data, predictors=pred_vars, outcome="outcome_sim", exc_sig=True, return_type="summary")

    >>> # Example 3: Return IV for all predictors (single plot)
    >>> vi.create_IV(pq_data, predictors=pred_vars, outcome="outcome_sim", exc_sig=False, return_type="plot")
    
    >>> # Example 4: Return WOE plots for all predictors
    >>> vi.create_IV(pq_data, predictors=pred_vars, outcome="outcome_sim", exc_sig=False, return_type="plot-WOE")
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

    # Perform statistical test
    predictors_pval = p_test(data=train, outcome=outcome, behavior=predictors["Variable"].tolist())
    
    # Filter significant predictors only if exc_sig is True
    if exc_sig:
        predictors_pval_filtered = predictors_pval[predictors_pval["pval"] <= siglevel]
        
        if predictors_pval_filtered.shape[0] == 0:
            raise ValueError("No predictors where the p-value lies below the significance level.")
        
        train = train[predictors_pval_filtered["Variable"].tolist() + [outcome]]
        predictors_to_use = predictors_pval_filtered["Variable"].tolist()
    else:
        # Use all predictors regardless of significance
        train = train[predictors_pval["Variable"].tolist() + [outcome]]
        predictors_to_use = predictors_pval["Variable"].tolist()

    # IV Analysis
    IV = map_IV(train, outcome, bins=bins, predictors=predictors_to_use)
    IV_names = list(IV["Tables"].keys())
    
    # Merge with p-values for final output (use appropriate filtered/unfiltered version)
    if exc_sig:
        IV_summary = pd.merge(IV["Summary"], predictors_pval_filtered, on="Variable")
    else:
        IV_summary = pd.merge(IV["Summary"], predictors_pval, on="Variable")
    
    IV_summary["pval"] = IV_summary["pval"].round(10)

    # Output loop
    if return_type == "summary":
        return IV_summary

    elif return_type == "IV":
        output_list = {variable: IV["Tables"][variable].assign(
            ODDS=lambda df: np.exp(df["WOE"] + lnodds),
            PROB=lambda df: df["ODDS"] / (df["ODDS"] + 1)) for variable in IV_names}
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
        return output_list
    else:
        raise ValueError("Please enter a valid input for `return_type`.")