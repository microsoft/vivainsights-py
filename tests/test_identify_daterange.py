import unittest
from vivainsights.identify_daterange import identify_datefreq
from vivainsights.pq_data import load_pq_data
import pandas as pd
import re

class TestIdentifyDateFreq(unittest.TestCase):

    def test_identify_datefreq(self):
        pq_data=load_pq_data()
        # Call the function to generate the return type data
        generated_output=identify_datefreq(pq_data['MetricDate'])
        # Check if the output is non empty text
        self.assertTrue(generated_output)
        # Check if the output is from existing list
        output_list = ["monthly", "weekly", "daily"]
        self.assertTrue(generated_output in output_list)

if __name__ == '__main__':
    unittest.main()