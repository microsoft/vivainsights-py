# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Create a network plot from a group-to-group query.
"""

__all__ = ['network_g2g']

import pandas as pd
from igraph import *
import igraph as ig
import matplotlib.pyplot as plt
import numpy as np
import re
import random

def network_g2g(data, primary=None, secondary=None, metric="Group_collaboration_time_invested", algorithm="fr", node_colour="lightblue", exc_threshold=0.1, org_count=None, node_scale = 1, edge_scale = 10, subtitle="Collaboration Across Organizations",figsize=None, return_type="plot"):
    """
    Return a network plot given a data frame containing a group-to-group query.

    Parameters
    ----------
    data : pandas.DataFrame
        Data frame containing a group-to-group query.
    primary : str, optional
        Variable name for the Primary Collaborator column. Auto-detected if ``None``.
    secondary : str, optional
        Variable name for the Secondary Collaborator column. Auto-detected if ``None``.
    metric : str
        Variable name for the collaboration metric. Defaults to ``"Group_collaboration_time_invested"``.
    algorithm : str
        Node placement algorithm. Defaults to ``"fr"`` (Fruchterman-Reingold).
    node_colour : str or dict
        Colour for displaying nodes. Defaults to ``"lightblue"``. If ``"vary"``,
        a random colour is assigned to each node. A dictionary can map specific
        node names to colours.
    exc_threshold : float
        Exclusion threshold between 0 and 1. Defaults to 0.1 (collaboration
        below 10 %% of a node's total is hidden). Has no impact on ``"data"``
        or ``"table"`` return.
    org_count : pandas.DataFrame, optional
        Data frame with two columns (group name and ``"n"``) providing the size
        of each organization. Defaults to ``None`` (fixed node sizes).
    node_scale : float
        Multiplier controlling node size. Defaults to 1.
    edge_scale : float
        Multiplier controlling edge width. Defaults to 10.
    subtitle : str
        Override for the default plot subtitle.
    figsize : tuple, optional
        Figure size as ``(width, height)`` in inches. Defaults to ``(8, 6)``.
    return_type : str
        Type of output to return. Valid values:

        - ``"plot"`` (default): matplotlib Figure.
        - ``"table"``: interaction matrix as a DataFrame.
        - ``"network"``: igraph object.
        - ``"data"``: long-format DataFrame of underlying data.

    Returns
    -------
    matplotlib.figure.Figure, pandas.DataFrame, or igraph.Graph
        Output depends on ``return_type``.

    Examples
    --------
    >>> import vivainsights as vi
    >>> # Return a network visual
    >>> vi.network_g2g(data=vi.load_g2g_data(), metric="Group_meeting_count")
    >>>
    >>> # Return the interaction matrix
    >>> vi.network_g2g(data=vi.load_g2g_data(), return_type="table")
    >>>
    >>> # No exclusion threshold
    >>> vi.network_g2g(data=vi.load_g2g_data(), exc_threshold=0)
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

        # return a 'tidy' matrix
        table = plot_data.pivot(index = "PrimaryOrg", columns = "SecondaryOrg", values = "metric_prop")
        return table
    
    elif return_type == "data":

        # return long table
        return plot_data
    
    elif return_type in ["plot", "network"]:

        # create network object - one for export, one for plotting
        # exclusion threshold ONLY applies in network output and plotting 
        mynet_em = plot_data[plot_data['metric_prop'] > exc_threshold]
        mynet_em.loc[:, ['PrimaryOrg', 'SecondaryOrg']] = mynet_em[['PrimaryOrg', 'SecondaryOrg']].apply(lambda func: func.str.replace(' ', '\n'))
        
        # a version of the graph without self-collaboration
        mynet_em_noloops = mynet_em[mynet_em['PrimaryOrg'] != mynet_em['SecondaryOrg']]
        mynet_em_noloops.loc[:, 'metric_prop'] = mynet_em_noloops['metric_prop'] * edge_scale # only scale width for the plotting graph
        
        # Set 'metric_props' as edge attribute
        g = ig.Graph.TupleList(mynet_em.itertuples(index=False), directed=False, edge_attrs = ['metric_prop'])
        g_noloops = ig.Graph.TupleList(mynet_em_noloops.itertuples(index=False), directed=False, edge_attrs = ['metric_prop'])
        
        # Org count can vary by size
        if org_count is not None:
            g.vs["org_size"] = (
                pd.DataFrame({"id": g.vs["name"]})
                .assign(id=lambda org: org["id"].str.replace("\n", " "))
                .merge(org_count, how="left", left_on="id", right_on=hrvar_string)
                .assign(n=lambda org: org["n"] / 100) #scale for plotting
                .loc[:, "n"]
                .tolist()
            )
            
            g_noloops.vs["org_size"] = (
                pd.DataFrame({"id": g_noloops.vs["name"]})
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
             
            g_noloops.vs['org_size'] = (
                pd.DataFrame({"id": g_noloops.vs['name']})
                .assign(id=lambda org: org['id'].str.replace('\n', ' '))
                .assign(n=0.4)
                .loc[:, 'n']
                .tolist()
            )

        # scale the size of the nodes
        g.vs["org_size"] = [x*node_scale for x in g.vs["org_size"]] 
        g_noloops.vs["org_size"] = [x*node_scale for x in g_noloops.vs["org_size"]]
        
        # Add edge_colour with transparent grey
        g_noloops.es["edge_colour"] = [(0.827, 0.827, 0.827, 0.5)] * g_noloops.ecount()


        if return_type == "network":
            return g # return 'igraph' object
        else:
            # Keep multiple edges, remove loops
            # g = g.simplify(multiple = True, loops = True)
            
            g = g_noloops # use version of graph with no self-collaboration
            
            # plot object
            fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))
            ig.plot(
                g,
                layout=g.layout(algorithm),
                target=ax,
                vertex_label=g.vs["name"],
                vertex_frame_width=0,
                vertex_size=g.vs["org_size"],
                vertex_color=setColor(node_colour, g.vs["name"]),  
                edge_width= g.es["metric_prop"],                
                # edge_width=mynet_em["metric_prop"] * 1,
                # edge_alpha=0.2,
                edge_color= g.es["edge_colour"]
            )
            
            plt.suptitle("Group to Group Collaboration" + '\n' + subtitle, fontsize=13)
            plt.figtext(0.95, 0.05, "Displays only collaboration above {}% of node's total collaboration".format(int(exc_threshold * 100)), ha="right", va="bottom", fontsize=8)     
            return fig
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