import unittest
import pandas as pd
from vivainsights import load_mt_data  # Replace with the actual module name

class TestLoadMeetingDataFunction(unittest.TestCase):
    def test_load_mt_data(self):
        # Test if the function returns a pandas DataFrame
        mt_data = load_mt_data()
        self.assertIsInstance(mt_data, pd.DataFrame)

        # Test if the DataFrame is not empty
        self.assertFalse(mt_data.empty)

if __name__ == '__main__':
    unittest.main()