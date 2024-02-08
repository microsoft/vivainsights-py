import unittest
from vivainsights.g2g_data import load_g2g_data
import pandas as pd


class TestGToGData(unittest.TestCase):

    def test_g2g_data(self):
        g2g_data=load_g2g_data()
        
        # Check if the table is not empty
        self.assertFalse(g2g_data.empty)

if __name__ == '__main__':
    unittest.main()