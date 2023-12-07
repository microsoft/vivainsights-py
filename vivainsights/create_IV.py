# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import wilcoxon
from vivainsights.create_bar_asis import create_bar_asis,plot_WOE
from vivainsights.p_test import p_test
from vivainsights.calculate_IV import map_IV

def create_IV(data, predictors=None, outcome=None, bins=5, siglevel=0.05, exc_sig=False, return_type="plot"):
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
    IV = map_IV(train,outcome, predictors=predictors_pval["Variable"].tolist())
    # map_IV(data, outcome, predictors=None, bins=10)

    IV_names = list(IV["Tables"].keys())

    IV_summary = pd.merge(IV["Summary"], predictors_pval, on="Variable")

    IV_summary["pval"]=IV_summary["pval"].round(10)

    if return_type == "summary":
        print("here summary")
        return IV_summary

    elif return_type == "IV":
        return {"IV": IV, "lnodds": lnodds}

    elif return_type == "plot":
        top_n = min(12, IV_summary.shape[0])
        create_bar_asis(IV_summary,
                        group_var="Variable",
                        bar_var="pval",
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
        pass
        # output_list = {
        #                 name: pd.DataFrame({
        #                 'ODDS': np.exp(IV[name]['WOE'] + IV[name]['lnodds']),
        #                 'PROB': IV[name]['ODDS'] / (IV[name]['ODDS'] + 1)})
        #                 for name in IV_names
        #                 }
        
        # output_list1 = {variable: IV["Tables"][variable].assign(
            # ODDS=lambda x: np.exp(x["WOE"] + lnodds),
            # PROB=lambda x: x["ODDS"] / (x["ODDS"] + 1)
            # ) for variable in IV_names}
        # output_list = {variable: df.set_index('Tables')[variable] for variable, df in output_list1.items()}
        # return output_list
    else:
        raise ValueError("Please enter a valid input for `return_type`.")
