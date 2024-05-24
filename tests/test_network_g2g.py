import unittest
import pandas as pd
import matplotlib.pyplot as plt
import vivainsights as vi
import warnings
import igraph as ig

class TestNetworkG2G(unittest.TestCase):
    def setUp(self):
        # set up g2g_data
        self.g2g_data = vi.load_g2g_data()

    def test_return_type_table(self):
        # Call the network_g2g function with return_type = "table"
        result = vi.network_g2g(data = self.g2g_data, return_type="table")
        
        # Check if the result is a pandas DataFrame
        self.assertIsInstance(result, pd.DataFrame)

    def test_return_type_data(self):

        with warnings.catch_warnings(record=True) as w: 
            # Call the network_g2g function with return_type = "data"
            result = vi.network_g2g(data = self.g2g_data, return_type="data")
        
            # Check if the result is a pandas DataFrame
            self.assertIsInstance(result, pd.DataFrame)

            # Check if any warnings were generated
            # self.assertLess(len(w), 1)

    def test_return_type_network(self):
            
        with warnings.catch_warnings(record=True) as w: 

            # Call the network_g2g function with return_type = "network"
            result = vi.network_g2g(data = self.g2g_data, return_type="network")
        
            # Check if the result is an iGraph graph
            self.assertIsInstance(result, ig.Graph)

            # Check if any warnings were generated
            # self.assertLess(len(w), 1)

    def test_return_type_plot(self):
        with warnings.catch_warnings(record=True) as w: 
            # Call the network_g2g function with return_type = "plot"
            result = vi.network_g2g(data = self.g2g_data, return_type="plot")
        
            # Check if a plot was created
            self.assertIsNotNone(plt.gcf())
            
            # Close all matplotlib windows
            plt.close('all')            

            # Check if any warnings were generated
            # self.assertLess(len(w), 1)

#run unit tests
if __name__ == '__main__':
    unittest.main()
