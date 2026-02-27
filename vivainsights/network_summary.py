# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Summarize node centrality statistics from an igraph network object.
"""

__all__ = ['network_summary']

from igraph import *
import igraph as ig
import pandas as pd
import matplotlib.pyplot as plt

def network_summary(graph, hrvar = None, return_type = "table"):
    """
    Summarise node centrality statistics from an igraph object.

    Parameters
    ----------
    graph : igraph.Graph
        Graph object returned from ``network_g2g()`` or ``network_p2p()``
        with ``return_type="network"``.
    hrvar : str, optional
        HR variable by which to split metrics. Defaults to ``None``.
    return_type : str
        Type of output to return. Valid values:

        - ``"table"`` (default): summary DataFrame.
        - ``"network"``: igraph object with centrality attributes added.
        - ``"plot"``: (not yet implemented).

    Returns
    -------
    pandas.DataFrame or igraph.Graph
        DataFrame with columns ``betweenness``, ``closeness``, ``degree``,
        ``eigenvector``, and ``pagerank``; or the enriched igraph object.

    Examples
    --------
    Return centrality metrics as a table:

    >>> import vivainsights as vi
    >>> graph = vi.network_g2g(data=vi.load_g2g_data(), return_type="network")
    >>> vi.network_summary(graph, hrvar="Organization", return_type="table")

    Return the enriched igraph network object:

    >>> vi.network_summary(graph, hrvar="Organization", return_type="network")
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

    # graph = graph.simplify() # Note: NOT simplified as simplification may remove too many edges

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