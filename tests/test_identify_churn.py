import unittest
from vivainsights import identify_churn
from vivainsights.pq_data import load_pq_data
import pandas as pd
import re

class TestIdentifyChurn(unittest.TestCase):

    def test_identify_churn(self):
        pq_data=load_pq_data()
        # Call the function to generate the return type data
        generated_output_data=identify_churn(pq_data,n1 = 6,n2 = 6,return_type="data",flip = False,date_column = "MetricDate",date_format = "%Y-%m-%d")
        # Check if the output is set
        self.assertTrue(isinstance(generated_output_data, set))
        # Call the function to generate the return type message
        generated_output_message=identify_churn(pq_data,n1 = 6,n2 = 6,return_type="message",flip = False,date_column = "MetricDate",date_format = "%Y-%m-%d")
        # Call the function to generate the return type text
        generated_output_text=identify_churn(pq_data,n1 = 6,n2 = 6,return_type="text",flip = False,date_column = "MetricDate",date_format = "%Y-%m-%d")
        # Check if the output is non empty text
        self.assertTrue(generated_output_text)
        

if __name__ == '__main__':
    unittest.main()