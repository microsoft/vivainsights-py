import unittest
import pandas as pd
from vivainsights import load_p2p_data  # Replace with the actual module name

class TestLoadP2PDataFunction(unittest.TestCase):
    def test_load_p2p_data(self):
        # Test if the function returns a pandas DataFrame
        result_data = load_p2p_data()
        self.assertIsInstance(result_data, pd.DataFrame)

        # Test if the DataFrame is not empty
        self.assertFalse(result_data.empty)

if __name__ == '__main__':
    unittest.main()
