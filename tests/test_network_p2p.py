import unittest
import pandas as pd
import matplotlib.pyplot as plt
import vivainsights as vi

class TestNetworkP2P(unittest.TestCase):
    def setUp(self):
        # Set up p2p_data
        self.p2p_data = vi.p2p_data_sim()    
    
    def test_return_type_table(self):
        # Call the network_p2p function with return_type = "table"
        result = vi.network_p2p(data = self.p2p_data, return_type="table")
        
        # Check if the result is a pandas DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_return_type_plot(self):  
        # Call the network_p2p function with return_type = "plot"
        vi.network_p2p(data = self.p2p_data, return_type="plot")
        
        # Check if a plot was created
        self.assertIsNotNone(plt.gcf())