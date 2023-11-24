import unittest
from vivainsights import extract_date_range
from vivainsights.pq_data import load_pq_data
import pandas as pd
import re

class TestExtractDateRange(unittest.TestCase):

    def test_generate_table_and_text(self):
        pq_data=load_pq_data()
        # Call the function to generate the table and text
        generated_table=extract_date_range(data=pq_data,return_type = "table")

        # Check if the table is not empty
        self.assertFalse(generated_table.empty)

        # Check if the DataFrame has the correct columns
        expected_columns = ["Start", "End"]
        self.assertListEqual(list(generated_table.columns), expected_columns)
        # Check if the columns has date values in the format 'YYYY-DD-MM'
        date_column = ['Start','End'] 
        for column in date_column:
            if column in generated_table.columns:
                date_values = generated_table[column]
                for date_value in date_values:
                    self.assertRegex(str(date_value), r'\d{4}-\d{2}-\d{2}')

        generated_text=extract_date_range(data=pq_data,return_type = "text")
        
        # Check if the text is not empty
        self.assertTrue(generated_text)
        date_format = r'\d{4}-\d{2}-\d{2}'
        expected_text_format = f'Data from {date_format} to {date_format}'
        
        # Check if the text is in pattern
        self.assertRegex(generated_text, expected_text_format)
        actual_dates = re.findall(date_format, generated_text)
        for date_str in actual_dates:
            pd.to_datetime(date_str) 

if __name__ == '__main__':
    unittest.main()