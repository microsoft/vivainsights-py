import unittest
import pandas as pd
import matplotlib.pyplot as plt
import vivainsights as vi
import igraph as ig
import plotly.graph_objects as go
import warnings
import tempfile
import os
import glob

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

    def test_custom_path_parameter(self):
        """Test that custom path parameter is respected and not overridden"""
        import tempfile
        import os
        import glob
        
        # Save current directory
        original_dir = os.getcwd()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                
                # Test with custom path
                custom_path = "my_custom_test_path"
                
                with warnings.catch_warnings(record=True) as w:
                    # Call network_p2p with custom path
                    vi.network_p2p(
                        data=self.p2p_data, 
                        path=custom_path,
                        return_type="plot-pdf"
                    )
                
                # Check generated files
                pdf_files = glob.glob("*.pdf")
                custom_files = [f for f in pdf_files if f.startswith(custom_path)]
                
                # Assert custom path was used
                self.assertGreater(len(custom_files), 0, 
                                 f"Expected file with custom path '{custom_path}' but found: {pdf_files}")
                
                # Check if any warnings were generated
                self.assertLess(len(w), 1)
                
        finally:
            # Restore original directory
            os.chdir(original_dir)
    
    def test_default_path_behavior(self):
        """Test that default path behavior is preserved when no custom path is provided"""
        import tempfile
        import os
        import glob
        
        # Save current directory
        original_dir = os.getcwd()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                
                with warnings.catch_warnings(record=True) as w:
                    # Test with empty string (default)
                    vi.network_p2p(
                        data=self.p2p_data, 
                        path="",
                        return_type="plot-pdf"
                    )
                
                # Check generated files start with default "p2p"
                pdf_files = glob.glob("*.pdf")
                default_files = [f for f in pdf_files if f.startswith("p2p_")]
                
                self.assertGreater(len(default_files), 0, 
                                 f"Expected file with default path 'p2p_' but found: {pdf_files}")
                
                # Check if any warnings were generated
                self.assertLess(len(w), 1)
                
        finally:
            # Restore original directory
            os.chdir(original_dir)

 # NOTE: Test is throwing errors because  create_sankey is not called correctly
 #   def test_return_type_sankey(self):
 #       # Call the network_p2p function with return_type = "sankey"
 #       vi.network_p2p(data = self.p2p_data, community= "leiden", return_type="sankey")
 #       #check if the result calls the create_sankey function correctly
 #       self.assertEqual(vi.network_p2p(data = self.p2p_data, community= "leiden", return_type="sankey"), vi.create_sankey(data = self.p2p_data, var1 = "Organization", var2 = "Organization"))


#run unit tests
if __name__ == '__main__':
    unittest.main()
