import unittest
import pandas as pd
import matplotlib.pyplot as plt
from vivainsights.keymetrics_scan import keymetrics_scan
from vivainsights.pq_data import load_pq_data

class TestKeyMetricsScan(unittest.TestCase):
    def setUp(self):
        # Load sample data for testing
        self.pq_data = load_pq_data()

    def test_keymetrics_scan_plot(self):
        result = keymetrics_scan(data=self.pq_data, hrvar='Organization', return_type='plot')
        self.assertIsInstance(result, plt.Figure)
        plt.close('all')  # Close the plot window after the test

    def test_keymetrics_scan_table(self):
        result = keymetrics_scan(data=self.pq_data, hrvar='Organization', return_type='table')
        self.assertIsInstance(result, pd.DataFrame)

if __name__ == '__main__':
    unittest.main()