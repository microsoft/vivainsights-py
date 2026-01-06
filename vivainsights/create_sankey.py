# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#Create a sankey chart from a two-column count table

__all__ = ['create_sankey']

import pandas as pd
import plotly.graph_objects as go
import random
def create_sankey(data, var1, var2, count = "n"):
    """   
    Name
    ----
    create_sankey

    Description
    ------------
    Create a 'networkD3' style sankey chart based on a long count table with two variables. The input data should have three columns, where each row is a unique group:
    1. Variable 1
    2. Variable 2
    3. Count
    
    Parameters
    ----------
    data : dataframe
        Data frame of the long count table.
    var1 : str 
        String containing the name of the variable to be shown on the left.
    var2 : str 
        String containing the name of the variable to be shown on the right.
    count : str
        String containing the name of the count variable.

    Returns
    -------
    A 'sankeyNetwork' and 'htmlwidget' object containing a two-tier sankey plot. The output can be saved locally with `htmlwidgets::saveWidget()`.
    
    Example
    -------
    >>> create_sankey(data = pq_data, var1 = "Organization", var2 = "FunctionType")
    """ 
    #Rename 
    data['pregroup'] = data[[var1]]
    data['group'] = data[[var2]]

    #Set up nodes
    group_source = data['pregroup'].unique()
    group_target = data['group'].unique() + " "

    nodes_source = pd.DataFrame({'name': group_source})
    nodes_target = pd.DataFrame({'name': group_target})
    nodes = pd.concat([nodes_source, nodes_target], axis=0)
    nodes = nodes.reset_index(drop=True)
    nodes["node"] = range(len(nodes))

    links = data.assign(group=data['group'] + " ")
    links = links.rename(columns={'pregroup': 'source', 'group': 'target', count: 'value'})
    links = links.loc[:, ['source', 'target', 'value']]

    sources = links['source'].unique()
    targets = links['target'].unique()

    source_colours = []
    target_colours = []
    
    for i in range(len(sources)):
        source_colours.append(f"#{random.randint(0, 0xFFFFFF):06x}")

    for i in range(len(targets)):
        target_colours.append(f"#{random.randint(0, 0xFFFFFF):06x}")


    #left join 
    # links = pd.merge(links, nodes_source, left_on='source', right_on='name', how='left')
    # links = pd.merge(links, nodes_target, left_on='target', right_on='name', how='left')
    
    '''Sankey diagram'''
    fig = go.Figure(data=[go.Sankey(
        
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes['name'],
            color = source_colours + target_colours
        ),

        link=dict(
            source=links['source'].map(nodes.set_index('name')['node']),
            target=links['target'].map(nodes.set_index('name')['node']),
            value=links['value'],
        ))]
    )
    
    fig.update_layout(title_text="Sankey Diagram of " + var1 + " and " + var2, font_size=10)
    fig.show()