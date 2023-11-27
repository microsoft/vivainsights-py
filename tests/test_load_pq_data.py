import unittest
import pandas as pd
from vivainsights import load_pq_data  # Replace with the actual module name

class TestLoadPQDataFunction(unittest.TestCase):
    def test_load_pq_data(self):
        
        # Test if the function returns a pandas DataFrame
        result_data = load_pq_data()
        self.assertIsInstance(result_data, pd.DataFrame)

        # Test if the DataFrame is not empty
        self.assertFalse(result_data.empty)

if __name__ == '__main__':
    unittest.main()
