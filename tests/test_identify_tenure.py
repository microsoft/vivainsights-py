import unittest
import pandas as pd
from faker import Faker
from vivainsights import identify_tenure 

class TestIdentifyTenureFunction(unittest.TestCase):
    def setUp(self):
        # Create a sample DataFrame for testing
        fake = Faker()
        data = {
                'PersonId': [i + 1 for i in range(5000)],
                'HireDate': [fake.date_this_decade() for _ in range(5000)],
                'MetricDate': [fake.date_between_dates(date_start=fake.date_this_decade()) for _ in range(5000)]
            }
        self.sample_df = pd.DataFrame(data)

    def test_identify_tenure_text_return(self):
        # Test if the function returns a text message
        result_text = identify_tenure(self.sample_df, return_type='text')
        expected_text = "tenure is"
        self.assertIn(expected_text, result_text)

    # def test_identify_tenure_plot_return(self):
    #     # Test if the function generates a plot
    #     with self.subTest():
    #         # Test if the function returns a plot
    #         with self.assertRaises(Exception):
    #             identify_tenure(self.sample_df, return_type='plot')

    def test_identify_tenure_cleaned_data_return(self):
        # Test if the function returns cleaned data
        cleaned_data = identify_tenure(self.sample_df, return_type='data_cleaned')
        self.assertIsInstance(cleaned_data, pd.DataFrame)

    def test_identify_tenure_dirty_data_return(self):
        # Test if the function returns dirty data
        dirty_data = identify_tenure(self.sample_df, return_type='data_dirty')
        self.assertIsInstance(dirty_data, pd.DataFrame)

if __name__ == '__main__':
    unittest.main()
