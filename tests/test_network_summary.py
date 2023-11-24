import unittest
from igraph import Graph
import pandas as pd
from vivainsights import network_summary
import vivainsights as vi
import igraph as ig

class TestNetworkSummaryFunction(unittest.TestCase):
    def setUp(self):
        # Data preparation for network_summary
        data=vi.p2p_data_sim()
        weight = None
        hrvar = "Organization"
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
        g=g_raw
        return(g)

    def test_network_summary_table_return(self):
        
        # Test if the function returns a table (pandas DataFrame)
        g=TestNetworkSummaryFunction.setUp(self)
        generated_object= vi.network_summary(g,hrvar = "Organization", return_type="table")
        self.assertIsInstance(generated_object, pd.DataFrame)
        
        # Test if the DataFrame has the expected columns
        expected_columns = ['node_id', 'betweenness', 'closeness', 'degree', 'eigenvector','pagerank', 'hrvar']
        self.assertListEqual(list(generated_object.columns), expected_columns)

        # Test if the DataFrame is not empty
        self.assertFalse(generated_object.empty)

    def test_network_summary_network_return(self):
        
        # Test if the function returns a network (igraph object)
        g=TestNetworkSummaryFunction.setUp(self)
        result_network = network_summary(g, return_type='network')
        self.assertIsInstance(result_network, Graph)

        # Test if node attributes are updated in the graph
        self.assertTrue(all(attr in result_network.vs.attributes() for attr in ['betweenness', 'closeness', 'degree', 'eigenvector', 'pagerank']))

    def test_network_summary_invalid_return_type(self):
        
        # Test if the function raises a ValueError for an invalid return type
        g=TestNetworkSummaryFunction.setUp(self)
        with self.assertRaises(ValueError):
            network_summary(g, return_type='invalid_type')

if __name__ == '__main__':
    unittest.main()