import unittest
import pandas as pd
from vivainsights import load_p2g_data

class TestLoadP2GDataFunction(unittest.TestCase):
    def test_load_p2g_data(self):
        
        # Test if the function returns a pandas DataFrame
        result_data = load_p2g_data()
        self.assertIsInstance(result_data, pd.DataFrame)

        # Test if the DataFrame is not empty
        self.assertFalse(result_data.empty)

if __name__ == '__main__':
    unittest.main()
