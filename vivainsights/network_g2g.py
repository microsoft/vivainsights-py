# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module returns a network plot given a data frame containing a group-to-group query.
"""
import pandas as pd
import igraph as ig
import numpy as np
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
    hrvar_string = re.sub("SecondaryCollaborator_", "",  string = secondary)

    #Warn if 'Within Group' is not in the data
    if "Within Group" not in data[secondary].unique().tolist():
        print("Warning: Within Group variable is not found in the " + secondary + " variable. The analysis may be excluding in-group collaboration.")

    #Run plot_data
    plot_data = data.rename(columns={primary: "PrimaryOrg", secondary: "SecondaryOrg", metric: "Metric"})
    plot_data = plot_data.assign(SecondaryOrg=np.where(plot_data.SecondaryOrg == "Within Group", plot_data.PrimaryOrg, plot_data.SecondaryOrg))    
    plot_data = plot_data.groupby(["PrimaryOrg", "SecondaryOrg"]).agg({"Metric": "mean"}).reset_index()
    plot_data = plot_data.query('PrimaryOrg != "Other_Collaborators" & SecondaryOrg != "Other_Collaborators"')
    plot_data = plot_data.groupby("PrimaryOrg")
    plot_data = plot_data.apply(lambda func: func.assign(metric_prop=func.Metric / func.Metric.sum())).reset_index(drop=True)
    plot_data = plot_data.loc[:, ["PrimaryOrg", "SecondaryOrg", "metric_prop"]]

    if return_type == "table":

        #return a 'tidy' matrix
        return plot_data.pivot(index = "PrimaryOrg", columns = "SecondaryOrg", values = "metric_prop")
    
    elif return_type == "data":

        #return long table
        return plot_data
    
    elif return_type in ["plot", "network"]:

        # network object
        mynet_em = plot_data[plot_data['metric_prop'] > exc_threshold]
        mynet_em.loc[:, ['PrimaryOrg', 'SecondaryOrg']] = mynet_em[['PrimaryOrg', 'SecondaryOrg']].apply(lambda func: func.str.replace(' ', '\n'))
        mynet_em.loc[:, 'metric_prop'] = mynet_em['metric_prop'] * 10
        
        g = ig.Graph.TupleList(mynet_em.itertuples(index=False), directed=False)
        
        #Org count can vary by size

        if org_count is not None:
            g.vs["org_size"] = (
                pd.DataFrame({"id": g.vs["name"]})
                .assign(id=lambda org: org["id"].str.replace("\n", " "))
                .merge(org_count, how="left", left_on="id", right_on=hrvar_string)
                .loc[:, "n"]
                .tolist()
            )

        else:
            #imputed size if not specified
             g.vs['org_size'] = (
                pd.DataFrame({"id": g.vs['name']})
                .assign(id=lambda org: org['id'].str.replace('\n', ' '))
                .assign(n=50)
                .loc[:, 'n']
                .tolist()
            )
             
        #plot object
        g = g.simplify() 
        plot_obj = ig.plot(
            g,
            title="Group to Group Collaboration",
            subtitle=subtitle,
            caption="",
            layout=g.layout(algorithm),
            vertex_label=g.vs["name"],
            vertex_size=g.vs["org_size"],
            vertex_frame_width=0,          
            vertex_color=node_colour,  
            edge_width=mynet_em["metric_prop"] * 1,
            edge_color="grey",
            edge_alpha=0.5,
            edge_curved=False,
            bbox=(1000, 1000), 
            margin=100, 
        )

        if return_type == "network":
            return g #return 'igraph' object
        
        #TODO: Custom Node Colours 
        #TODO: Auto assign colours
        #TODO: Return 'plot' object

    else:
        raise ValueError("Please enter a valid input for 'return'.")
