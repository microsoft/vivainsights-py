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
from matplotlib.legend_handler import HandlerTuple
import matplotlib.lines as mlines
from matplotlib.backends.backend_pdf import PdfPages
import random
from sklearn.preprocessing import minmax_scale
import warnings
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
    legend_pos = "best",
    palette = "rainbow",
    node_alpha = 0.7,
    edge_alpha = 1,
    edge_col = "#777777",
    node_sizes = [1, 20],
    node_scale = 1,
    seed = 1,
    legend_ncols=0,
    figsize: tuple = None
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
        - `"multilevel"` (a version of louvain)
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
        
    bg_fill : str 
        String to specify background fill color.
    font_col : str
        String to specify font color.
    legend_pos : str
        String to specify position of legend. Valid values include:  
        String to specify position of legend. Valid values include: 
        - `"best"`
        - `"upper right"`
        - `"upper left"`
        - `"lower left"`
        - `"right"`
        -  `"center left"`
        - `"center right"`
        - `"lower center"`
        - `"upper center"`
        - `"center"`
    palette : str 
        String specifying the function to generate a color palette with a single argument `n`. Uses `"rainbow"` by default.
    node_alpha : int 
        A numeric value between 0 and 1 to specify the transparency of the nodes. Defaults to 0.7.
    :param edge_alpha : int
        A numeric value between 0 and 1 to specify the transparency of the edges (only for 'ggraph' mode). Defaults to 1.
    edge_col: String to specify edge link color.
    node_sizes: int
        Numeric vector of length two to specify the range of node sizes to rescale to, when `centrality` is set to a non-null value.
    node_scale: int
        A numeric value to multiply or divide the size of the nodes. 
        This is applied to the 'node_size' attribute in the graph to increase or decrease the size of the nodes.
    seed : int
        Seed for the random number generator passed to either `set.seed()` when the louvain or leiden community detection algorithm is used, to ensure consistency. Only applicable when `community` is set to one of the valid non-null values.
    legend_ncols : int
        Value is either 0 or 1, Parameter to change the orientation horizontal to vertical of legend in the plot.
    figsize : tuple
        The `figsize` parameter is an optional tuple that specifies the size of the figure for the boxplot visualization. It should be in the format `(width, height)`, where `width` and `height` are in inches. If not provided, a default size of (8, 6) will be used.
        
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
    >>> import vivainsights as vi
    >>> sample_data = vi.p2p_data_sim()
    >>> # Return a network visual
    >>> vi.network_p2p(data = sample_data, return_type = "plot")

    >>>  # Return the vertex table with counts in communities and HR attribute
    >>> # Resolution is set to a low value to yield fewer communities
    >>> vi.network_p2p(data = sample_data, community = "leiden", comm_args = {"resolution": 0.01}, return_type = "table")
    
    >>> # Return the vertex table with centrality calculations
    >>> vi.network_p2p(data = sample_data, centrality = "betweenness", return_type = "table")
    
    >>> vi.network_p2p(
    >>>    data = sample_data, # or whatever your query is stored
    >>>    node_scale = 50, # adjust this parameter to make nodes bigger/smaller
    >>>    return_type = "plot"
    >>>    )
    
    >>> # Return the sankey output based on centrality and community
    >>> vi.network_p2p(
    >>>    data = sample_data, # or whatever your query is stored
    >>>    return_type = "sankey", # another return type for visualization 
    >>>    centrality = "betweenness", # centrality can be set as per requirement
    >>>    community = "leiden" # Adjust community 
    >>>    )
    
    >>> # Return the plot output based on different color scheme, legend orientation and position, font color change
    >>> vi.network_p2p(
    >>>    data = sample_data, # or whatever your query is stored
    >>>    return_type = "plot",
    >>>    font_col = "grey20", # Color change option for fonts in chart
    >>>    legend_pos = "upper left", # Adjust the legend position using this parameter
    >>>    legend_ncols = 1 # Adjust this parameter to 0 or 1 to change legend orientation from vertical to horizontal
    >>>    )
    
    """
    path ="p2p" + ("" if community is None else '_' + community)
    
    # `style` is currently a placeholder as only igraph is supported
    # legacy argument from the R implementation
    style = "igraph"

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
        
        # g = g_raw.simplify()
        g = g_raw # Note: NOT simplified as simplification may remove too many edges
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
        # g = g_ud.simplify()
        g = g_ud # Note: NOT simplified as simplification may remove too many edges
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
        g.vs["node_size"] = node_sizes/100 #scale for plotting      
    elif centrality is None:
        # all nodes with the same size if centrality is not calculated
        # adjust for plotting formats
        if style == "igraph":
            g.vs["node_size"] = [0.08] * g.vcount()
        elif style == "ggraph":
            g.vs["node_size"] = [0.08] * g.vcount()
            node_sizes = [0.03,0.03] #fix node size
    else:
        raise ValueError("Please enter a valid input for `centrality`.")

    # Common area ------------------- ----------------
    # vertex table
    vert_ft = vert_ft.rename(columns = {"node": "name"})    
    
    if centrality is not None:
        if community is None:
            vert_tb = pd.DataFrame({
                "name": g.vs["name"],
                "betweenness": g.vs["betweenness"],
                "closeness": g.vs["closeness"],
                "degree": g.vs["degree"],
                "eigenvector": g.vs["eigenvector"],
                "pagerank": g.vs["pagerank"],
            })
        else :
            vert_tb = pd.DataFrame({
                "name": g.vs["name"],
                "cluster": g.vs[v_attr],
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
    
    g_layout = g.layout(layout)

    out_path = path + '_' + time.strftime("%y%m%d_%H%M%S") + '.pdf'

    # Return outputs ---------------------------------------
    #use fast plotting method
    if return_type in ["plot", "plot-pdf"]:
        
        def rainbow(n):
            return [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(n)]
            
        # Set colours
        vert_tb = vert_tb.drop_duplicates()
        
        colour_tb = (
            pd.DataFrame({v_attr: g.vs[v_attr]})
             .assign(colour = eval(f"{palette}(len(vert_tb))"))
        )

        # Colour vector
        colour_v = (
            pd.DataFrame({v_attr: g.vs[v_attr]})
            .merge(colour_tb, on = v_attr, how = "left")
            .loc[:, "colour"]
        )

        if style == "igraph":
            # Set graph plot colours
            # color_names = list(mcolors.CSS4_COLORS.keys())
            # g.vs["color"] = [mcolors.to_rgba(color_names[i % len(color_names)], alpha=node_alpha) for i in range(len(g.vs))]
    
            g.vs["frame_color"] = None
            g.es["width"] = 1

            #Internal basic plotting function used inside 'network_p2p()'
            def plot_basic_graph(lpos = legend_pos, pdf=False, node_scale=node_scale):
                
                fig, ax = plt.subplots(figsize=figsize if figsize else (8, 6))
                plt.rcParams["figure.facecolor"] = bg_fill
                layout_func = getattr(ig.Graph, f"layout_{layout}")
                
                # Get the unique values of the vertex attribute
                unique_values = list(set(g.vs[v_attr]))
                
                # Create a colormap with one color for each unique value
                cmap = mcolors.ListedColormap([plt.get_cmap('tab20')(i) for i in range(len(unique_values))])

                handles = []
                labels = []
                
                # Map each unique value to an index in the colormap
                value_to_index = {value: i for i, value in enumerate(unique_values)}
                
                # Legend
                for i, value in enumerate(unique_values):
                    marker = mlines.Line2D([0], [0], marker='o', color='w', label=value, markerfacecolor=cmap(i), markersize=5)
                    handles.append(marker)
                    labels.append(value)
                    
                # Set node colours
                for i, value in enumerate(g.vs[v_attr]):
                    index = value_to_index[g.vs[i][v_attr]]
                    color = cmap(index)
                    g.vs[i]["color"] = color

                g.vs["node_size"] = [x*node_scale for x in g.vs["node_size"]] # scale the size of the nodes
                
                ig.plot(
                    g,
                    layout = layout_func(g),
                    target=ax,
                    vertex_label = None,
                    vertex_size = g.vs["node_size"],
                    edge_arrow_mode = "0",
                    edge_arrow_size=0, 
                    edge_color = "#adadad",
                )              
                
                # Number of legend columns
                if legend_ncols==0:
                    if len(handles)<=10:
                        leg_cols=len(handles)
                    elif 10<len(handles)<=20:
                        leg_cols = (len(handles) // 2)
                    else:
                        leg_cols = (len(handles) // 4)
                        warnings.warn("There are over 20 unique node categories. Consider changing your grouping variable, merging existing groups, or tweaking algorithm parameters (if applicable).", UserWarning)
                else:
                    leg_cols=1
                    
                plt.legend(
                    handles = handles,
                    labels = labels,
                    handler_map={tuple: HandlerTuple(ndivide=20)},
                    loc = legend_pos,
                    edgecolor= edge_col,
                    frameon = True,
                    markerscale = 1,
                    fontsize= 5,
                    labelcolor = 'grey',
                    ncols = leg_cols
                )

                if pdf:
                    return fig
                
                return plt.show() #return 'ggplot' object

            # Default PDF output unless None supplied to path
            if return_type == "plot":
                
                plot_basic_graph(lpos = legend_pos)
                
            elif return_type == "plot-pdf":
                with PdfPages(out_path) as pdf:
                    pdf.savefig(plot_basic_graph(pdf=True))
                print(f"Saved to {out_path}.")

        else:
            raise ValueError("Invalid input for `style`.")
    
    elif return_type == "data":
        
        vert_tb = vert_tb.reset_index(drop = True) 
        
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