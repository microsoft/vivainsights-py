# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This module performs network analysis with a person-to-person query
"""
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from community import community_louvain
from datetime import datetime
import vivainsights as vi
import igraph as ig
from matplotlib import cm
from sklearn.preprocessing import minmax_scale
import random



def network_p2p(data,
                hrvar="Organization",
                return_type="plot",
                centrality=None,
                community=None,
                weight=None,
                layout="mds",
                path=None,
                style="igraph",
                legend_pos="best",
                palette="rainbow",
                color_by=None,
                edge_alpha=1,
                edge_col="#777777",
                comm_args = None,
                node_sizes=(1, 10),
                seed=1):
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
        
    bg_fill : str 
        String to specify background fill colour.
    font_col : str
        String to specify font colour.
    legend_pos : str
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
    # Return a network visual
    vi.network_p2p(data = p2p_data, return_type = "plot")
    
    # Return the vertex table with counts in communities and HR attribute
    vi.network_p2p(data = p2p_data, community = "leiden", comm_args = {"resolution": 0.01}, return_type = "table")
    """
    path ="p2p" + ("" if community is None else '_' + community)
    
    # `style` is currently a placeholder as only igraph is supported
    # legacy argument from the R implementation
    style="igraph"
    
    G = nx.Graph()
    # Create edges and add nodes
    for index, row in data.iterrows():
        G.add_edge(row["PrimaryCollaborator_PersonId"], row["SecondaryCollaborator_PersonId"], weight=row[weight] if weight else 10)
    if len(node_sizes) != 2: raise ValueError("`node_sizes` must be of length 2")

    # Set data frame for edges
    edges = data.assign(NoWeight=1).loc[:, ["PrimaryCollaborator_PersonId", "SecondaryCollaborator_PersonId", "NoWeight"]].rename(columns={"NoWeight": "weight"}) if weight is None else data.loc[:, ["PrimaryCollaborator_PersonId", "SecondaryCollaborator_PersonId", weight]]

    pc_hrvar, sc_hrvar = "PrimaryCollaborator_" + hrvar, "SecondaryCollaborator_" + hrvar
    
    color_by="PrimaryCollaborator_" + hrvar

    if return_type in ("network","data","table","sankey"):
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
                # Name of vertex attribute
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
            #a djust for plotting formats
            if style == "igraph":
                g.vs["node_size"] = [0.08] * g.vcount()
            elif style == "ggraph":
                g.vs["node_size"] = [0.08] * g.vcount()
                node_sizes = [0.03,0.03] #fix node size
        else:
            raise ValueError("Please enter a valid input for `centrality`.")
    
        vert_ft = vert_ft.rename(columns = {"node": "name"})    
    
        if centrality is not None:
            if community is None:
                vertex_df = pd.DataFrame({
                    "name": g.vs["name"],
                    "betweenness": g.vs["betweenness"],
                    "closeness": g.vs["closeness"],
                    "degree": g.vs["degree"],
                    "eigenvector": g.vs["eigenvector"],
                    "pagerank": g.vs["pagerank"],
                })
            else :
                vertex_df = pd.DataFrame({
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
                vertex_df = pd.DataFrame({
                    "name": g.vs["name"],
                })
            else:
                vertex_df = pd.DataFrame({
                    "name": g.vs["name"],
                    "cluster": g.vs[v_attr]
                })
    
        vertex_df = vertex_df.merge(vert_ft, on = "name", how = "left").drop_duplicates()
    
    # Community detection
    if community:
        partition = community_louvain.best_partition(G, weight='weight', random_state=seed)
        nx.set_node_attributes(G, partition, 'cluster')
    g_raw = ig.Graph.TupleList(edges.itertuples(index=False), directed=True, weights=True)
    # Centrality calculations
    if centrality:
        if centrality == 'betweenness':
            centrality_values = nx.betweenness_centrality(G, weight='weight')
        elif centrality == 'closeness':
            centrality_values = nx.closeness_centrality(G)
        elif centrality == 'degree':
            centrality_values = dict(G.degree(weight='weight'))
        elif centrality == 'eigenvector':
            centrality_values = nx.eigenvector_centrality(G, weight='weight')
        elif centrality == 'pagerank':
            centrality_values = nx.pagerank(G, weight='weight')

        min_centrality = min(centrality_values.values())
        max_centrality = max(centrality_values.values())
        node_sizes = [node_sizes[0] + (node_sizes[1] - node_sizes[0]) * (centrality_values[node] - min_centrality) / (max_centrality - min_centrality)
                      for node in G.nodes()]
    else:
        node_sizes = [node_sizes[0]] * len(G.nodes())

    if color_by is not None:
        if data[color_by].dtype == "object":
            # Create a mapping of unique character values to distinct colors
            duplicate_guids = data[data.duplicated(subset='PrimaryCollaborator_PersonId', keep=False)]
            l=len(data['PrimaryCollaborator_PersonId'].drop_duplicates())
            no_dup=data['PrimaryCollaborator_PersonId'].drop_duplicates()
            m=len(data['SecondaryCollaborator_PersonId'].drop_duplicates())
            no_dup1=data['SecondaryCollaborator_PersonId'].drop_duplicates()
            no_dup2=pd.concat([no_dup,no_dup1])
            no_dup2=no_dup2.drop_duplicates()
            lst=[]
            for value in no_dup:
                p=(data.loc[data['PrimaryCollaborator_PersonId']==value,'PrimaryCollaborator_Organization'])
                lst.append(p.values[0])
            if len(G.nodes())!= len(lst):
                lst=[]
                for value in no_dup2:
                    q=(data.loc[(data['PrimaryCollaborator_PersonId']==value ) | (data['SecondaryCollaborator_PersonId']==value),'PrimaryCollaborator_Organization'])
                    lst.append(q.values[0])
            temp_set= list(set(lst))
            cmap = cm.get_cmap(palette)
            colors=[cmap(i / len(temp_set)) for i in range(len(temp_set))]
            value_to_int={temp_set[i]: colors[i] for i in range(len(colors))}
            unique_colors_names=list(value_to_int.keys())
            unique_colors=list(value_to_int.values())
            node_colors = [value_to_int[category] for category in lst]
        else:
            node_colors = [row[color_by] for _, row in data.iterrows()]
    else:
        node_colors = "blue"


    # Layout
    if layout == "mds":
        pos = nx.layout.spring_layout(G)
    elif layout == "circular":
        pos = nx.layout.circular_layout(G)
    elif layout == "kamada_kawai":
        pos = nx.layout.kamada_kawai_layout(G)
    else:
        pos = nx.layout.spring_layout(G)

    # Plotting
    node_size = 20 if centrality is None else [v * 2 for v in centrality_values.values()] if centrality == "degree" else [v * 20000 for v in centrality_values.values()]
    # Handling different return types
    if return_type == "plot" or return_type == "plot-pdf":    
    # Display the network plot using Matplotlib
        plt.figure(figsize=(10, 10))
        if style == "igraph":
            node_size = 20 if centrality is None else [v * 2 for v in centrality_values.values()] if centrality == "degree" else [v * 20000 for v in centrality_values.values()]
            edge_width = 1
            if community:
                clusters = [G.nodes[node]['cluster'] for node in G.nodes()]
                edge_width = 0.5
                cmap = plt.get_cmap(palette, max(clusters))
                node_colors = [cmap(cluster / max(clusters)) for cluster in clusters]
                unique_clusters = list(set(clusters))
                legend_patches = [mpatches.Patch(color=cmap(cluster / max(clusters)), label=f'Cluster {cluster}') for cluster in unique_clusters]
                plt.legend(handles=legend_patches, title="Cluster Legend", loc=legend_pos,bbox_to_anchor=(1.05, 1))
            nx.draw(G, pos, node_color=node_colors, node_size=node_size, with_labels=False,
                    edge_color=edge_col, alpha=edge_alpha, width=edge_width)
            if community == None:
                legend_patches = [mpatches.Patch(color=(unique_colors[i]), label=label) for i, label in enumerate(unique_colors_names)]
                plt.legend(handles=legend_patches, title=f'{color_by} Legend',  loc=legend_pos, bbox_to_anchor=(1.05, 1), ncol=len(unique_colors_names))
            plt.title("Person-to-Person Network Analysis")
            
            if return_type == "plot":
                plt.show()
            elif return_type == "plot-pdf":
                path = path if path else f"p2p_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                plt.savefig(path, format="pdf",bbox_inches='tight')
                print(f"Saved plot to {path}")
    elif return_type == "sankey":
        if community is None:
            raise ValueError("Note: no sankey return option is available if `None` is selected at `community`. Please specify a valid community detection algorithm.")
        elif community in valid_comm:
            vi.create_sankey(data = vertex_df.groupby([hrvar, 'cluster']).size().reset_index(name='n'), var1=hrvar, var2='cluster')
    elif return_type == "table":
        if community is None:
            if centrality is None:
                vertex_df = vertex_df.groupby(hrvar).size().reset_index(name='n')
            else:
                vertex_df = vertex_df.groupby(hrvar).agg(
                    n=('betweenness', 'size'),
                    betweenness=('betweenness', 'mean'),
                    closeness=('closeness', 'mean'),
                    degree=('degree', 'mean'),
                    eigenvector=('eigenvector', 'mean'),
                    pagerank=('pagerank', 'mean')
                )
        elif community in valid_comm:
            if centrality is None:
                vertex_df = vertex_df.groupby([hrvar, 'cluster']).size().reset_index(name='n')
            else:
                vertex_df = vertex_df.groupby([hrvar, 'cluster']).agg(
                    n=('betweenness', 'size'),
                    betweenness=('betweenness', 'mean'),
                    closeness=('closeness', 'mean'),
                    degree=('degree', 'mean'),
                    eigenvector=('eigenvector', 'mean'),
                    pagerank=('pagerank', 'mean')
            )
                
        return vertex_df
    elif return_type == "data":
        vertex_df = vertex_df.reset_index(drop = True) 
        return vertex_df
    elif return_type == "network":
        return g
    else :
        raise ValueError("invalid input for `return_type`.")