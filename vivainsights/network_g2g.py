# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module returns a network plot given a data frame containing a group-to-group query.
"""
import pandas as pd
import igraph as ig
import matplotlib.pyplot as plt 
import seaborn as sns
import re

def network_g2g(data, primary=None, secondary=None, metric="Meeting_Count", algorithm="fr", node_colour="lightblue", exc_threshold=0.1, org_count=None, subtitle="Collaboration Across Organizations", return_type="plot"):
    if primary is None:
        #Only return first match
        primary = data.filter(regex = "^PrimaryCollaborator_").columns[0] 
        print("Primary field not provided. Assuming {} as the primary variable.".format(primary))

    if secondary is None:
        #Only return first match
        secondary = data.filter(regex = "^SecondaryCollaborator_").columns[0]
        print("Secondary field not provided. Assuming {} as the secondary variable.".format(secondary))

    #Get string of HR variable (for grouping)
    hrvar_string = re.sub(pattern = "SecondaryCollaborator_", replacement = "",  string = secondary)

    #Warn if 'Within Group' is not in the data
    if "WithinGroup" not in data[secondary].unique():
        print("Warning: WithinGroup variable is not found in the " + secondary + " variable. The analysis may be excluding in-group collaboration.")

    #Run plot_data
    plot_data = data.rename(columns = {primary: "PrimaryOrg", secondary: "SecondaryOrg", metric: "Metric"})
    plot_data = plot_data.assign(SecondaryOrg = lambda org: org.PrimaryOrg if org.SecondaryOrg == "Within Group" else org.SecondaryOrg)
    plot_data = plot_data.groupby(["PrimaryOrg", "SecondaryOrg"]).agg({"Metric": "mean"}).reset_index()
    plot_data = plot_data.groupby("PrimaryOrg")
    plot_data = plot_data.apply(lambda func: func.assign(metric_prop = func.Metric / func.Metric.sum())).reset_index(drop = True)
    plot_data = plot_data.loc[:, ["PrimaryOrg", "SecondaryOrg", "metric_prop"]]

    if return_type == "table":

        #return a 'tidy' matrix
        return plot_data.pivot(index = "PrimaryOrg", columns = "SecondaryOrg", values = "metric_prop")
    
    elif return_type == "data":

        #return long table
        return plot_data
    
