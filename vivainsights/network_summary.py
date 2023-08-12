# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module summarises node centrality statistics with an igraph object
"""
from igraph import *
import igraph as ig
import pandas as pd
import matplotlib.pyplot as plt

def network_summary(graph, hrvar = None, return_type = "table"):
    """
    Name
    ----
    network_summary

    Description
    ------------
    This function summarises node centrality statistics with an igraph object.

    Parameters
    ----------
    graph : igraph object
        'igraph' object that can be returned from `network_g2g()` or `network_p2p()` when the `return` argument is set to `"network"`.
    hrvar : str 
        String containing the name of the HR Variable by which to split metrics. Defaults to `None`.
    return_type : str 
        String specifying what output to return. Valid inputs include:
        - `"table"`
        - `"network"`
        - `"plot"`
   
    Returns
    -------
    By default, a data frame containing centrality statistics. Available statistics include:
    - `betweenness`: number of shortest paths going through a node.
    - `closeness`: number of steps required to access every other node from a given node.
    - `degree`: number of connections linked to a node.
    - `eigenvector`: a measure of the influence a node has on a network.
    - `pagerank`: calculates the PageRank for the specified vertices.

    Examples
    --------
    >>> graph = network_g2g(data = vi.load_g2g_data(), return_type = "network")
    >>> network_summary(graph, hrvar = "Organization", return_type = "table")
    """ 
    #calculate summary table
    sum_tb = pd.DataFrame({
        "node_id":  graph.vs["name"],
        "betweenness": graph.betweenness(),
        "closeness": graph.closeness(),
        "degree": graph.degree(),
        "eigenvector": graph.evcent(),
        "pagerank": graph.pagerank()
    })

    if(hrvar is not None):
        sum_tb['hrvar'] = graph.vs[hrvar]

    graph = graph.simplify() 

    if return_type == "table":
        return sum_tb #return table

    elif return_type == "network":
        graph.vs["betweenness"] = sum_tb["betweenness"]
        graph.vs["closeness"] = sum_tb["closeness"]
        graph.vs["degree"] = sum_tb["degree"]
        graph.vs["eigenvector"] = sum_tb["eigenvector"]
        graph.vs["pagerank"] = sum_tb["pagerank"]

        return graph #return network

    elif return_type == "plot":
        if hrvar is None:
            raise ValueError("Visualisation options currently only available when a valid HR attribute is supplied.")
        else:
            return #TODO: return plot
    else: 
        raise ValueError("Invalid input to `return`")