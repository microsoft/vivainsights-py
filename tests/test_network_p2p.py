import unittest
import pandas as pd
import matplotlib.pyplot as plt
import vivainsights as vi
import igraph as ig
import plotly.graph_objects as go
import warnings

class TestNetworkP2P(unittest.TestCase):
    def setUp(self):
        # Set up p2p_data
        self.p2p_data = vi.p2p_data_sim()    
    
    def test_return_type_table(self):

        with warnings.catch_warnings(record=True) as w:
            # Call the network_p2p function with return_type = "table"
            result = vi.network_p2p(data = self.p2p_data, return_type="table")
        
            # Check if the result is a pandas DataFrame
            self.assertIsInstance(result, pd.DataFrame)

            # Check if any warnings were generated
            self.assertLess(len(w), 1)

        
    def test_return_type_plot(self): 

        with warnings.catch_warnings(record=True) as w: 
            # Call the network_p2p function with return_type = "plot"
            result = vi.network_p2p(data = self.p2p_data, return_type="plot")
        
            # Check if a plot was created
            self.assertIsNotNone(plt.gcf())

            # Check if any warnings were generated
            self.assertLess(len(w), 1)
    
    def test_return_type_data(self):

        with warnings.catch_warnings(record=True) as w: 
            # Call the network_p2p function with return_type = "data"
            result = vi.network_p2p(data = self.p2p_data, return_type="data")
        
            # Check if the result is a pandas DataFrame
            self.assertIsInstance(result, pd.DataFrame)

            # Check if any warnings were generated
            self.assertLess(len(w), 1)

    def test_return_type_network(self):

        with warnings.catch_warnings(record=True) as w: 

            # Call the network_p2p function with return_type = "network"
            result = vi.network_p2p(data = self.p2p_data, return_type="network")
        
            # Check if the result is an iGraph graph
            self.assertIsInstance(result, ig.Graph)

            # Check if any warnings were generated
            self.assertLess(len(w), 1)

    def test_return_type_sankey(self):
        # Call the network_p2p function with return_type = "sankey"
        vi.network_p2p(data = self.p2p_data, community= "leiden", return_type="sankey")
        #check if the result calls the create_sankey function correctly
        self.assertEqual(vi.network_p2p(data = self.p2p_data, community= "leiden", return_type="sankey"), vi.create_sankey(data = self.p2p_data, var1 = "Organization", var2 = "Organization"))


#run unit tests
if __name__ == '__main__':
    unittest.main()
