import unittest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from vivainsights.create_lorenz import *
from vivainsights.pq_data import load_pq_data

class TestCreateLorenz(unittest.TestCase):
    """
    Test that the create_lorenz function returns all the expected output types
    """

    def setUp(self):
        # Load DataFrame for testing
        self.pq_data = load_pq_data()   

    def test_create_lorenz_gini(self):
        result = create_lorenz(self.pq_data, metric='Emails_sent', return_type='gini')
        self.assertIsInstance(result, float)

    def test_create_lorenz_table(self):
        result = create_lorenz(self.pq_data, metric='Emails_sent', return_type='table')
        self.assertIsInstance(result, pd.DataFrame)

    def test_create_lorenz_plot(self):
        result = create_lorenz(self.pq_data, metric='Emails_sent', return_type='plot')
        self.assertIsInstance(result, plt.Figure)
        plt.close('all')  # Close the plot window after the test

if __name__ == '__main__':
    unittest.main()