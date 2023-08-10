# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module performs network analysis with a person-to-person query
"""
import pandas as pd
import igraph as ig
import matplotlib.pyplot as plt
import random

def network_p2p(data, 
    hrvar = "Organization",
    return_type = "plot",
    centrality = None,
    community = None,
    weight = None,
    comm_args = None,
    layout = "mds",
    path = "",
    style = "igraph",
    bg_fill = "#FFFFFF",
    font_col = "grey20",
    legend_pos = "right",
    palette = "rainbow",
    node_alpha = 0.7,
    edge_alpha = 1,
    edge_col = "#777777",
    node_sizes = [1, 20],
    seed = 1
):
    """
    :param data: Data frame containing a person-to-person query.
    :param hrvar: String containing the label for the HR attribute.
    :param return_type: A different output is returned depending on the value passed to the `return_type`
    argument:
    - `'plot'` (default)
    - `'plot-pdf'`
    - `'sankey'`
    - `'table'`
    - `'data'`
    - `'network'`

    :param centrality: string to determines which centrality measure is used to scale the size of the nodes. All centrality measures are automatically calculated when it is set to one of the below values, and reflected in the `'network'` and `'data'` outputs.
    Measures include:
    - `betweenness`
    - `closeness`
    - `degree`
    - `eigenvector`
    - `pagerank`
    When `centrality` is set to None, no centrality is calculated in the outputs and all the nodes would have the same size. 

    :param community: String determining which community detection algorithms to apply. Valid values include:
    - `None` (default): compute analysis or visuals without computing communities.
    - `"louvain"`
    - `"leiden"`
    - `"edge_betweenness"`
    - `"fast_greedy"`
    - `"fluid_communities"`
    - `"infomap"`
    - `"label_prop"`
    - `"leading_eigen"`
    - `"optimal"`
    - `"spinglass"`
    - `"walk_trap"`

    :param weight: String to specify which column to use as weights for the network. To create a graph without weights, supply `None` to this argument.
    :param comm_args: list containing the arguments to be passed through to igraph's clustering algorithms. Arguments must be named. See examples section on how to supply arguments in a named list.
    :param layout: String to specify the node placement algorithm to be used. Defaults to `"mds"` for the deterministic multi-dimensional scaling of nodes. 
    See <https://rdrr.io/cran/ggraph/man/layout_tbl_graph_igraph.html> for a full  list of options.
    :param path: File path for saving the PDF output. Defaults to a timestamped path based on current parameters.
    :param style: String to specify which plotting style to use for the network plot. Valid values include:
    - `"igraph"`
    - `"ggraph"`

    :param bg_fill: String to specify background fill colour.
    :param font_col: String to specify font colour.
    :param legend_pos: String to specify position of legend. Defaults to
    `"right"`. See `ggplot2::theme()`. This is applicable for both the 'ggraph' and the fast plotting method. Valid inputs include:
    - `"bottom"`
    - `"top"`
    - `"left"`
    -`"right"`

    :param palette: String specifying the function to generate a colour palette with a single argument `n`. Uses `"rainbow"` by default.
    :param node_alpha: A numeric value between 0 and 1 to specify the transparency of the nodes. Defaults to 0.7.
    :param edge_alpha: A numeric value between 0 and 1 to specify the transparency of the edges (only for 'ggraph' mode). Defaults to 1.
    :param edge_col: String to specify edge link colour.
    :param node_sizes: Numeric vector of length two to specify the range of node sizes to rescale to, when `centrality` is set to a non-null value.
    :param seed: Seed for the random number generator passed to either `set.seed()` when the louvain or leiden community detection algorithm is used, to ensure consistency. Only applicable when `community` is set to one of the valid non-null values.

    :return: A different output is returned depending on the value passed to the `return_type` argument:
    - `'plot'`: return a network plot, interactively within R.
    - `'plot-pdf'`: save a network plot as PDF. This option is recommended when the graph is large, which make take a long time to run if `return_type = 'plot'` is selected. Use this together with `path` to control the save location.
    - `'sankey'`: return a sankey plot combining communities and HR attribute. This is only valid if a community detection method is selected at community`.
    - `'table'`: return a vertex summary table with counts in communities and HR attribute. When `centrality` is non-NULL, the average centrality values are calculated per group.
    - `'data'`: return a vertex data file that matches vertices with communities and HR attributes.
    - `'network'`: return 'igraph' object.
    """
    path ="p2p" + ("" if community is None else '_' + community)

    if len(node_sizes) > 2:
        raise ValueError("`node_sizes` must be of length 2")

    #Set data frame for edges
    if weight is None:
        edges = data.assign(NoWeight = 1).loc[:, ["PrimaryCollaborator_PersonId", "SecondaryCollaborator_PersonId", "NoWeight"]].rename(columns = {"NoWeight": "weight"})

    else:
        edges = data.loc[:, ["PrimaryCollaborator_PersonId", "SecondaryCollaborator_PersonId", weight]]

    #Set variables
    #TieOrigin = PrimaryCollabortor
    tieOrigin = edges[["PrimaryCollaborator_PersonId"]].drop_duplicates().rename(columns={"PrimaryCollaborator_PersonId": "node"})
    #TieDest = SecondaryCollaborator
    tieDest = edges[["SecondaryCollaborator_PersonId"]].drop_duplicates().rename(columns={"SecondaryCollaborator_PersonId": "node"})
    
    pc_hrvar = "PrimaryCollaborator_" + hrvar
    sc_hrvar = "SecondaryCollaborator_" + hrvar

    #Vertices data frame to provide meta-data
    vert_ft = pd.concat([tieOrigin, tieDest])

    #left join to add HR variable
    vert_ft = vert_ft.merge(data[["PrimaryCollaborator_PersonId", pc_hrvar]], left_on="node", right_on="PrimaryCollaborator_PersonId", how="left").drop_duplicates()
    vert_ft = vert_ft.merge(data[["SecondaryCollaborator_PersonId", sc_hrvar]], left_on="node", right_on="SecondaryCollaborator_PersonId", how="left").drop_duplicates()
    vert_ft = vert_ft.drop(columns=["PrimaryCollaborator_PersonId", "SecondaryCollaborator_PersonId"]) # Remove duplicate columns

    #Create igraph object
    g_raw = ig.Graph.TupleList(edges.itertuples(index=False), directed=True, weights=True)
    for vertex in vert_ft["node"]:
        g_raw.add_vertex(vertex)

    #Assign weights
    g_raw.es["weight"] = edges["weight"]

    # allowed community values
    valid_comm = ["leiden", "louvain", "edge_betweenness", "fast_greedy", "fluid_communities", "infomap", "label_prop", "leading_eigen", "optimal", "spinglass", "walk_trap"]

    # Finalise `g` object
    # If community detection is selected, this is where the communities are appended
    if community is None:
        g = g_raw.simplify()
        v_attr = hrvar
    elif community in valid_comm:
        random.seed(seed)
        g_ud = g_raw.as_undirected() # Convert to undirected graph
        alg_label = "igraph::cluster_" + community
        
        #combine arguments to clustering algorithms
        c_comm_args = ["graph", g_ud] + list(comm_args)
        comm_out = getattr(ig.clustering, community)(*c_comm_args)

        for i, vertex in enumerate(g_raw.vs): #add partition to graph object
            vertex["cluster"] = str(comm_out.membership[i])
        g = g_raw.simplify()

        #output communities object

        v_attr = "cluster"
    else: 
        raise ValueError("Please enter a valid input for `community`.")
    
    # centrality calculations ------------------------
    # attach centrality calculations if `centrality` is not NULL
    if centrality is not None:
        return #TODO
    else:
        return #TODO

    # Common area -----------------------------------
    ## Create vertex table