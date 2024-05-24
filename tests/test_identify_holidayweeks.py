import unittest
import pandas as pd
import matplotlib.pyplot as plt
import vivainsights as vi
import warnings

class TestIdentifyHolidayweeks(unittest.TestCase):
    def setUp(self):
        # set up pq_data
        self.pq_data = vi.load_pq_data()
        
    def test_return_type_text(self):
        with warnings.catch_warnings(record=True) as w:
            result = vi.identify_holidayweeks(data = self.pq_data, return_type="text")
            
            # Check if the result is a string
            self.assertIsInstance(result, str)        
        
            # Check if any warnings were generated
            self.assertLess(len(w), 1)
        
    def test_return_type_holidayweeks_data(self):
        result = vi.identify_holidayweeks(data=self.pq_data, return_type="holidayweeks_data")
        
        # Check if the result is a Pandas DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_return_type_data_cleaned(self):
        result = vi.identify_holidayweeks(data=self.pq_data, return_type="data_cleaned")
        
        # Check if the result is a Pandas DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_return_type_data_dirty(self):
        result = vi.identify_holidayweeks(data=self.pq_data, return_type="data_dirty")
        
        # Check if the result is a Pandas DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_return_type_plot(self):
        result = vi.identify_holidayweeks(data=self.pq_data, return_type="plot")
        
        # Check if the result is a Matplotlib plot
        self.assertIsInstance(result, plt.Figure)
        
        # Close all matplotlib windows
        plt.close('all')        
            
            