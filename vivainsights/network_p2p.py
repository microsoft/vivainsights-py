# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module performs network analysis with a person-to-person query
"""
import vivainsights as vi
import pandas as pd
import igraph as ig
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_pdf import PdfPages
import random
from sklearn.preprocessing import minmax_scale
import time

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
    Name
    ----
    network_p2p

    Description
    ------------
    This function returns a network plot given a data frame containing a person-to-person query.

    Parameters
    ----------
    data : dataframe 
        Data frame containing a person-to-person query.
    hrvar : str 
        String containing the label for the HR attribute.
    return_type : str 
        A different output is returned depending on the value passed to the `return_type` argument:
        - `'plot'` (default)
        - `'plot-pdf'`
        - `'sankey'`
        - `'table'`
        - `'data'`
        - `'network'`

    centrality : str 
        string to determines which centrality measure is used to scale the size of the nodes. All centrality measures are automatically calculated when it is set to one of the below values, and reflected in the `'network'` and `'data'` outputs. 
        Measures include:
        - `betweenness`
        - `closeness`
        - `degree`
        - `eigenvector`
        - `pagerank`
        When `centrality` is set to None, no centrality is calculated in the outputs and all the nodes would have the same size. 

    community : str 
        String determining which community detection algorithms to apply. Valid values include:
        - `None` (default): compute analysis or visuals without computing communities.
        - `"multilevel (a version of louvain)"`
        - `"leiden"`
        - `"edge_betweenness"`
        - `"fastgreedy"`
        - `"infomap"`
        - `"label_propagation"`
        - `"leading_eigenvector"`
        - `"optimal_modularity"`
        - `"spinglass"`
        - `"walk_trap"`

    weight : str 
        String to specify which column to use as weights for the network. To create a graph without weights, supply `None` to this argument.
    comm_args : list
        list containing the arguments to be passed through to igraph's clustering algorithms. Arguments must be named. See examples section on how to supply arguments in a named list.
    layout : str
        String to specify the node placement algorithm to be used. Defaults to `"mds"` for the deterministic multi-dimensional scaling of nodes. 
        See <https://rdrr.io/cran/ggraph/man/layout_tbl_graph_igraph.html> for a full  list of options.
    path : str (file path)
        File path for saving the PDF output. Defaults to a timestamped path based on current parameters.
    style: str 
        String to specify which plotting style to use for the network plot. Valid values include:
        - `"igraph"`
        - `"ggraph"`

    bg_fill : str 
        String to specify background fill colour.
    font_col : str
        String to specify font colour.
    legend_pos : str
        String to specify position of legend. Defaults to `"right"`. See `ggplot2::theme()`. This is applicable for both the 'ggraph' and the fast plotting method. Valid inputs include:
        - `"bottom"`
        - `"top"`
        - `"left"`
        -`"right"`

    palette : str 
        String specifying the function to generate a colour palette with a single argument `n`. Uses `"rainbow"` by default.
    node_alpha : int 
        A numeric value between 0 and 1 to specify the transparency of the nodes. Defaults to 0.7.
    :param edge_alpha : int
        A numeric value between 0 and 1 to specify the transparency of the edges (only for 'ggraph' mode). Defaults to 1.
    edge_col: String to specify edge link colour.
    node_sizes: int
        Numeric vector of length two to specify the range of node sizes to rescale to, when `centrality` is set to a non-null value.
    seed : int
        Seed for the random number generator passed to either `set.seed()` when the louvain or leiden community detection algorithm is used, to ensure consistency. Only applicable when `community` is set to one of the valid non-null values.

    Returns
    -------
    A different output is returned depending on the value passed to the `return_type` argument:
    - `'plot'`: return a network plot, interactively within R.
    - `'plot-pdf'`: save a network plot as PDF. This option is recommended when the graph is large, which make take a long time to run if `return_type = 'plot'` is selected. Use this together with `path` to control the save location.
    - `'sankey'`: return a sankey plot combining communities and HR attribute. This is only valid if a community detection method is selected at community`.
    - `'table'`: return a vertex summary table with counts in communities and HR attribute. When `centrality` is non-NULL, the average centrality values are calculated per group.
    - `'data'`: return a vertex data file that matches vertices with communities and HR attributes.
    - `'network'`: return 'igraph' object.

    Examples
    --------
    """
    path ="p2p" + ("" if community is None else '_' + community)

    if len(node_sizes) != 2:
        raise ValueError("`node_sizes` must be of length 2")

    #Set data frame for edges
    if weight is None:
        edges = data.assign(NoWeight = 1).loc[:, ["PrimaryCollaborator_PersonId", "SecondaryCollaborator_PersonId", "NoWeight"]].rename(columns = {"NoWeight": "weight"})

    else:
        edges = data.loc[:, ["PrimaryCollaborator_PersonId", "SecondaryCollaborator_PersonId", weight]]

    pc_hrvar = "PrimaryCollaborator_" + hrvar
    sc_hrvar = "SecondaryCollaborator_" + hrvar

    # TieOrigin = PrimaryCollaborator
    tieOrigin = (
        edges[["PrimaryCollaborator_PersonId"]].drop_duplicates()
        .merge(data[["PrimaryCollaborator_PersonId", pc_hrvar]], on = "PrimaryCollaborator_PersonId", how = "left") #left join
        .rename(columns = {"PrimaryCollaborator_PersonId": "node"})
        .assign(**{hrvar: lambda row: row[pc_hrvar]}) #assign new column
        .drop(columns = [pc_hrvar]) 
    )

    # TieDest = SecondaryCollaborator
    tieDest = (
        edges[["SecondaryCollaborator_PersonId"]].drop_duplicates()
        .merge(data[["SecondaryCollaborator_PersonId", sc_hrvar]], on = "SecondaryCollaborator_PersonId", how = "left")
        .rename(columns = {"SecondaryCollaborator_PersonId": "node"})
        .assign(**{hrvar: lambda row: row[sc_hrvar]})
        .drop(columns = [sc_hrvar])
    )

    # Vertices data frame to provide meta-data
    vert_ft = pd.concat([tieOrigin, tieDest]).drop_duplicates()

    # Create igraph object
    g_raw = ig.Graph.TupleList(edges.itertuples(index=False), directed=True, weights=True)

    # debugging
    if return_type == "g_raw":
        return g_raw
    elif return_type == "vert_ft":
        return vert_ft

    # Assign vertex attributes - HR attribute and node
    g_raw.vs[hrvar] = vert_ft[hrvar].tolist()
    g_raw.vs["node"] = vert_ft["node"].tolist()

    # Assign weights
    g_raw.es["weight"] = edges["weight"]

    # allowed community values
    valid_comm = ["leiden", "multilevel", "edge_betweenness", "fastgreedy", "infomap", "label_propagation", "leading_eigenvector", "optimal_modularity", "spinglass", "walk_trap"]

    # Finalise `g` object
    # If community detection is selected, this is where the communities are appended
    if community is None:
        g = g_raw.simplify()
        v_attr = hrvar 
        
    elif community in valid_comm:
        random.seed(seed)
        g_ud = g_raw.as_undirected() # Convert to undirected graph
        
        # combine arguments to clustering algorithms
        comm_func = getattr(ig.Graph, "community_" + community)
        if comm_args is None:
            comm_args = {}

        # call community detection function
        comm_out = comm_func(graph = g_ud, **comm_args)
        g = g_ud.simplify()
        g.vs["cluster"] = [str(member) for member in comm_out.membership]

        #Name of vertex attribute
        v_attr = "cluster"
    else: 
        raise ValueError("Please enter a valid input for `community`.")
        
    # centrality calculations ------------------------
    # valid values of `centrality`
    valid_cent = ['betweenness', 'closeness', 'degree', 'eigenvector', 'pagerank']  
    
    # attach centrality calculations if `centrality` is not None
    if centrality in valid_cent:
        g = vi.network_summary(g, return_type="network")
        node_sizes = (node_sizes[1] - node_sizes[0]) 
        node_sizes *= minmax_scale(g.vs[centrality]) + node_sizes #min and max values
        g.vs["node_size"] = node_sizes
    elif centrality is None:
        # all nodes with the same size if centrality is not calculated
        #a djust for plotting formats
        if style == "igraph":
            g.vs["node_size"] = [3] * g.vcount()
        elif style == "ggraph":
            g.vs["node_size"] = [2.5] * g.vcount()
            node_sizes = [3,3] #fix node size
    else:
        raise ValueError("Please enter a valid input for `centrality`.")

    # Common area ------------------- ----------------
    # vertex table
    vert_ft = vert_ft.rename(columns = {"node": "name"})    
    
    if centrality is not None:
        vert_tb = pd.DataFrame({
            "name": g.vs["name"],
            # "cluster": g.vs[v_attr], # commented out as `cluster` does not exist without comm detection
            "betweenness": g.vs["betweenness"],
            "closeness": g.vs["closeness"],
            "degree": g.vs["degree"],
            "eigenvector": g.vs["eigenvector"],
            "pagerank": g.vs["pagerank"],
        })
    else:
        if community is None:
            vert_tb = pd.DataFrame({
                "name": g.vs["name"],
            })
        else:
            vert_tb = pd.DataFrame({
                "name": g.vs["name"],
                "cluster": g.vs[v_attr]
            })

    vert_tb = vert_tb.merge(vert_ft, on = "name", how = "left").drop_duplicates() #merge hrvar to vertex table
    print("Printing merged vert_tb")
    print(vert_tb)
    
    g_layout = g.layout(layout)

    out_path = path + '_' + time.strftime("%y%m%d_%H%M%S") + '.pdf'

    # Return outputs ---------------------------------------
    #use fast plotting method
    if return_type in ["plot", "plot-pdf"]:
        
        def rainbow(n):
            return [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(n)]
            
        #Set colours
        
        # GET ALL ATTRIBUTES IN VERT_TB
        vert_tb = vert_tb.drop_duplicates()
        print(vert_tb)
        print(g.vertex_attributes())
        
        colour_tb = (
            pd.DataFrame({v_attr: g.vs[v_attr]})
             .assign(colour = eval(f"{palette}(len(vert_tb))"))
        )

        #Colour vector
        colour_v = (
            pd.DataFrame({v_attr: g.vs[v_attr]})
            .merge(colour_tb, on = v_attr, how = "left")
            .loc[:, "colour"]

        )

        if style == "igraph":
            #Set graph plot colours
            color_names = list(mcolors.CSS4_COLORS.keys())
            g.vs["color"] = [mcolors.to_rgba(color_names[i % len(color_names)], alpha=node_alpha) for i in range(len(g.vs))]
    
            g.vs["frame_color"] = None
            g.es["width"] = 1

            #Internal basic plotting function used inside 'network_p2p()'
            def plot_basic_graph(lpos = legend_pos):
                plt.rcParams["figure.facecolor"] = bg_fill
                layout_func = getattr(ig.Graph, f"layout_{layout}")
                #Legend position
                if lpos == "left":
                    leg_x = -1.5
                    leg_y = 0.5
                elif lpos == "right":
                    leg_x = 1.5
                    leg_y = 0.5
                elif lpos == "top":
                    leg_x = 0
                    leg_y = 1.5
                elif lpos == "bottom":
                    leg_x = 0
                    leg_y = -1.0
                else:
                    raise ValueError("Invalid input for `legend_pos`.")
                
                plot = ig.plot(
                    g,
                    layout = g.layout('kk'),
                    vertex_label = None,
                    vertex_size = g.vs["node_size"],
                    edge_arrow_mode = "-",
                    edge_color = "#adadad"
                )

                return plot.save('plot.png')
            
                # plt.legend(
                #     bbox_to_anchor = (leg_x, leg_y),
                #     #legend
                #     #handles= pch?
                #     labelcolor = font_col,
                #     #handlecolor = edge_col,
                #     #pt.bg
                #     #pt.cex
                #     #cex
                #     #bty
                #     ncol = 1

               # )

            # Default PDF output unless None supplied to path
            if return_type == "plot":
                plot_basic_graph()
            elif return_type == "plot-pdf":
                with PdfPages(out_path) as pdf:
                    plot_basic_graph()
                    pdf.savefig()
                print(f"Saved to {out_path}.")

        else:
            raise ValueError("Invalid input for `style`.")
    
    elif return_type == "data":
        vert_tb = vert_tb.reset_index(drop = True) 
        if centrality is None:
            vert_tb = vert_tb.drop(columns = "cluster")       
        return vert_tb
    
    elif return_type == "network":
        return g
    
    elif return_type == "sankey":
        if community is None:
            raise ValueError("Note: no sankey return option is available if `None` is selected at `community`. Please specify a valid community detection algorithm.")
        elif community in valid_comm:
            vi.create_sankey(data = vert_tb.groupby([hrvar, 'cluster']).size().reset_index(name='n'), var1=hrvar, var2='cluster')
    
    elif return_type == "table":
        if community is None:
            if centrality is None:
                vert_tb = vert_tb.groupby(hrvar).size().reset_index(name='n')
            else:
                vert_tb = vert_tb.groupby(hrvar).agg(
                    n=('betweenness', 'size'),
                    betweenness=('betweenness', 'mean'),
                    closeness=('closeness', 'mean'),
                    degree=('degree', 'mean'),
                    eigenvector=('eigenvector', 'mean'),
                    pagerank=('pagerank', 'mean')
                )
        elif community in valid_comm:
            if centrality is None:
                vert_tb = vert_tb.groupby([hrvar, 'cluster']).size().reset_index(name='n')
            else:
                vert_tb = vert_tb.groupby([hrvar, 'cluster']).agg(
                    n=('betweenness', 'size'),
                    betweenness=('betweenness', 'mean'),
                    closeness=('closeness', 'mean'),
                    degree=('degree', 'mean'),
                    eigenvector=('eigenvector', 'mean'),
                    pagerank=('pagerank', 'mean')
            )
                
        return vert_tb
            
    else:
        raise ValueError("invalid input for `return_type`.")