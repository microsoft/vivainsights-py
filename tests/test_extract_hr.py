import unittest
from vivainsights import extract_hr
from vivainsights.pq_data import load_pq_data
import pandas as pd


class TestExtractHr(unittest.TestCase):

    def test_extract_hr(self):
        pq_data=load_pq_data()
        # Call the function to generate the table and text
        generated_table=extract_hr(pq_data, max_unique =50, exclude_constants =True, return_type = "vars")

        # Check if the table is not empty
        self.assertFalse(generated_table.empty)

        generated_text=extract_hr(pq_data, max_unique =50, exclude_constants =True, return_type = "names")
        
        # Check if the text is not empty
        self.assertFalse(generated_text)

if __name__ == '__main__':
    unittest.main()