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
from vivainsights.create_bar_asis import create_bar_asis,plot_WOE
from vivainsights.p_test import p_test
from vivainsights.calculate_IV import map_IV
import warnings
warnings.filterwarnings("ignore")

def create_IV(data, predictors=None, outcome=None, bins=5, siglevel=0.05, exc_sig=False, return_type="plot"):
    """
    Name
    -----
    create_IV 
    
    Description
    -----------
    The code defines a function `create_IV` that calculates and visualizes the mean of a selected
    Specify an outcome variable and return IV outputs.    

    Parameters
    ----------
    data : pandas dataframe
        person query data
    predictors : str
        name of the metric to be analysed
    outcome : str
        name of the organizational attribute to be used for grouping
    bins: int
    siglevel: float
    exc_sig: boolean
    return_type: str
    
    Returns
    -------
    _type_
        the type of output to return. Defaults to "plot".
        the type of output to return. "summary".
        the type of output to return. "list".
        the type of output to return. "plot-WOE".
        the type of output to return. "IV".
        

    Example
    -------
    >>> import numpy as np

    >>> df["X"] = np.where(df["Internal_network_size"] > 40, 1, 0)
    >>> result = create_IV(df, predictors=["Email_hours",
    >>>                            "Meeting_hours",
    >>>                            "Chat_hours"
    >>>                         ], outcome="X",exc_sig=False, return_type="IV")

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

    
    predictors = pd.DataFrame({'Variable': np.array(train.columns)})

    predictors = predictors[predictors['Variable'] != 'outcome'].reset_index(drop=True)

    predictors['Variable'] = predictors['Variable'].astype(str)

    predictors_pval=p_test(data=train, outcome='X', behavior=["Email_hours","Chat_hours","Meeting_hours"])

    predictors_pval = predictors_pval[predictors_pval["pval"] <= siglevel]

    if predictors_pval.shape[0] == 0:
        raise ValueError("No predictors where the p-value lies below the significance level.")
    train = train[predictors_pval["Variable"].tolist() + [outcome]]

    # IV Analysis
    IV = map_IV(train,outcome,bins=bins,predictors=predictors_pval["Variable"].tolist())
    # map_IV(data, outcome, predictors=None, bins=10)

    IV_names = list(IV["Tables"].keys())

    IV_summary = pd.merge(IV["Summary"], predictors_pval, on="Variable")

    IV_summary["pval"]=IV_summary["pval"].round(10)

    if return_type == "summary":
        print(IV_summary)
        return (IV_summary)

    elif return_type == "IV":
        output_list = {variable: IV["Tables"][variable].assign(
            ODDS=lambda df: np.exp(df["WOE"] + lnodds),
            PROB=lambda df: df["ODDS"] / (df["ODDS"] + 1)) for variable in IV_names}
        for key, df in output_list.items():
            print(f" {key} :\n",f"{df}\n")
        print(f"Summary : \n {IV_summary}\n")
        print(f"lnodds:{lnodds}")
        return(output_list,IV_summary,lnodds)

    elif return_type == "plot":
        top_n = min(12, IV_summary.shape[0])
        create_bar_asis(IV_summary,
                        group_var="Variable",
                        bar_var="IV",
                        title="Information Value (IV)",
                        subtitle=("Showing top",top_n,"predictors"),
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