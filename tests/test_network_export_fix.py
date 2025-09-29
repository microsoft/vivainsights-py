import unittest
import os
import matplotlib.pyplot as plt
import vivainsights as vi

class TestNetworkExport(unittest.TestCase):
    """Test that network_p2p and network_g2g plots can be exported using export()"""
    
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = 'test_network_export'
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Set up test data
        self.p2p_data = vi.p2p_data_sim()
        self.g2g_data = vi.load_g2g_data()

    def tearDown(self):
        # Clean up matplotlib figures
        plt.close('all')
        
        # Remove the temporary directory and its contents
        for file_name in os.listdir(self.test_dir):
            file_path = os.path.join(self.test_dir, file_name)
            os.remove(file_path)
        os.rmdir(self.test_dir)

    def test_network_p2p_returns_figure(self):
        """Test that network_p2p returns a matplotlib Figure object"""
        plot = vi.network_p2p(data=self.p2p_data, return_type="plot")
        
        # Check that it returns a matplotlib Figure object
        self.assertIsInstance(plot, plt.Figure)
        
        # Check that it has the savefig method (required by export())
        self.assertTrue(hasattr(plot, 'savefig'))

    def test_network_g2g_returns_figure(self):
        """Test that network_g2g returns a matplotlib Figure object"""
        plot = vi.network_g2g(data=self.g2g_data, return_type="plot")
        
        # Check that it returns a matplotlib Figure object
        self.assertIsInstance(plot, plt.Figure)
        
        # Check that it has the savefig method (required by export())
        self.assertTrue(hasattr(plot, 'savefig'))

    def test_network_p2p_export_display(self):
        """Test that network_p2p plots can be displayed using export()"""
        plot = vi.network_p2p(data=self.p2p_data, return_type="plot")
        
        # This should not raise an error
        try:
            vi.export(plot, file_format='display')
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success, "export() with display format should work for network_p2p plots")

    def test_network_g2g_export_display(self):
        """Test that network_g2g plots can be displayed using export()"""
        plot = vi.network_g2g(data=self.g2g_data, return_type="plot")
        
        # This should not raise an error
        try:
            vi.export(plot, file_format='display')
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success, "export() with display format should work for network_g2g plots")

    def test_network_p2p_export_png(self):
        """Test that network_p2p plots can be saved as PNG using export()"""
        plot = vi.network_p2p(data=self.p2p_data, return_type="plot")
        file_path = os.path.join(self.test_dir, "test_p2p")
        
        # Export to PNG
        vi.export(plot, file_format='png', path=file_path, timestamp=False)
        
        # Check if the file was created
        expected_file = file_path + '.png'
        self.assertTrue(os.path.exists(expected_file), f"PNG file should be created at {expected_file}")

    def test_network_g2g_export_png(self):
        """Test that network_g2g plots can be saved as PNG using export()"""
        plot = vi.network_g2g(data=self.g2g_data, return_type="plot")
        file_path = os.path.join(self.test_dir, "test_g2g")
        
        # Export to PNG
        vi.export(plot, file_format='png', path=file_path, timestamp=False)
        
        # Check if the file was created
        expected_file = file_path + '.png'
        self.assertTrue(os.path.exists(expected_file), f"PNG file should be created at {expected_file}")

    def test_network_p2p_export_auto_behavior(self):
        """Test that network_p2p plots work with auto behavior (should display)"""
        plot = vi.network_p2p(data=self.p2p_data, return_type="plot")
        
        # This should not raise an error and should default to display behavior
        try:
            vi.export(plot, file_format='auto')
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success, "export() with auto behavior should work for network_p2p plots")

    def test_network_g2g_export_auto_behavior(self):
        """Test that network_g2g plots work with auto behavior (should display)"""
        plot = vi.network_g2g(data=self.g2g_data, return_type="plot")
        
        # This should not raise an error and should default to display behavior
        try:
            vi.export(plot, file_format='auto')
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success, "export() with auto behavior should work for network_g2g plots")


if __name__ == '__main__':
    unittest.main()