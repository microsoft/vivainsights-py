# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module returns a network plot given a data frame containing a group-to-group query.
"""
import pandas as pd
from igraph import *
import igraph as ig
import matplotlib.pyplot as plt
import numpy as np
import re
import random

def network_g2g(data, primary=None, secondary=None, metric="Meeting_Count", algorithm="fr", node_colour="lightblue", exc_threshold=0.1, org_count=None, subtitle="Collaboration Across Organizations", return_type="plot"):
    """
    Name
    ----
    network_g2g

    Description
    ------------
    This function returns a network plot given a data frame containing a group-to-group query.

    Parameters
    ----------
    data : data frame
        Data frame containing a group-to-group query.
    primary : str
        String containing the variable name for the Primary Collaborator column.
    secondary : str
        String containing the variable name for the SecondaryCollaborator column.
    metric: str
        String containing the variable name for metric. Defaults to `Meeting_Count`.
    algorithm : str
        String to specify the node placement algorithm to be used. 
        - Defaults to `"fr"` for the force-directed algorithm of Fruchterman and Reingold. 
        - See <https://rdrr.io/cran/ggraph/man/layout_tbl_graph_igraph.html> for a full list of options.
    node_colour : str or dictionary 
        String or named vector to specify the colour to be used for displaying nodes. 
        - Defaults to `"lightblue"`. 
        - If `"vary"` is supplied, a different colour is shown for each node at random. 
        - If a named dictionary is supplied, the names must match the values of the variable provided for the `primary` and `secondary` columns. 
        - See example section for details.
    exc_threshold: Numeric value between 0 and 1 specifying the exclusion threshold to apply. 
        - Defaults to 0.1, which means that the plot will only display collaboration above 10% of a node's total collaboration. 
        - This argument has no impact on `"data"` or `"table"` return.
    org_count : optional 
        Optional data frame to provide the size of each organizationin the `secondary` attribute. 
        - The data frame should contain only two columns: 
        - Name of the `secondary` attribute excluding any prefixes, e.g. `"Organization"`. 
        - Must be of character or factor type. `"n"`. Must be of numeric type. 
        - Defaults to `None`, where node sizes will be fixed.
    subtitle : str 
        String to override default plot subtitle.
    return_type : str
        String specifying what to return. This must be one of the following strings:
        - `"plot"`
        - `"table"`
        - `"network"`
        - `"data"`
        - Defaults to `"plot"`.

    Returns
    -------
    A different output is returned depending on the value passed to the `return` argument:
    - `"plot"`: 'ggplot' object. A group-to-group network plot.
    - `"table"`: data frame. An interactive matrix of the network.
    - `"network`: 'igraph' object used for creating the network plot.
    - `"data"`: data frame. A long table of the underlying data.

    Example
    -------
    >>> network_g2g(data = vi.load_g2g_data(), metric = "Meeting_Count")
    """ 
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
        table = plot_data.pivot(index = "PrimaryOrg", columns = "SecondaryOrg", values = "metric_prop")
        return table
    
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
                .assign(n=lambda org: org["n"] / 100) #scale for plotting
                .loc[:, "n"]
                .tolist()
            )
        else:
            #imputed size if not specified
             g.vs['org_size'] = (
                pd.DataFrame({"id": g.vs['name']})
                .assign(id=lambda org: org['id'].str.replace('\n', ' '))
                .assign(n=0.4)
                .loc[:, 'n']
                .tolist()
            )

        if return_type == "network":
            return g #return 'igraph' object
        else:
            #plot object
            g = g.simplify()
            fig, ax = plt.subplots(figsize=(8, 8))
            ig.plot(
                g,
                layout=g.layout(algorithm),
                target=ax,
                vertex_label=g.vs["name"],
                vertex_frame_width=0,
                vertex_size=g.vs["org_size"],
                vertex_color=setColor(node_colour, g.vs["name"]),  
                edge_width=mynet_em["metric_prop"] * 1,
                edge_alpha=0.5,
                edge_color="grey",
            )
            
            plt.suptitle("Group to Group Collaboration" + '\n' + subtitle, fontsize=13)
            plt.figtext(0.95, 0.05, "Displays only collaboration above {}% of node's total collaboration".format(int(exc_threshold * 100)), ha="right", va="bottom", fontsize=8)     
            return plt.show() #return 'ggplot' object
    else:
        raise ValueError("Please enter a valid input for 'return'.")
    
def setColor(node_colour, org):
    org = [i.replace("\n", " ") for i in org]
    if isinstance(node_colour, str) and len(node_colour) > 1:
        if node_colour == "vary": #generate a random colour for each node in the network
            node_colour = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(len(org))]
        else:
            node_colour = node_colour #use the colour provided
    elif isinstance(node_colour, dict): #use dictionary to map each node to a colour
        node_colour = {node: colour for node, colour in node_colour.items()}
        for node, colour in node_colour.items():
            if colour == "random": 
                node_colour[node] = f"#{random.randint(0, 0xFFFFFF):06x}"
            else:
                node_colour[node] = colour
        node_colour = [node_colour.get(node, "lightblue") for node in org] #use default colour if key not found

    else: #default colour
        node_colour = "lightblue"

    return node_colour