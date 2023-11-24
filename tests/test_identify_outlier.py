import unittest
from  vivainsights.identify_outlier import identify_outlier
from vivainsights.pq_data import load_pq_data
import pandas as pd

class TestIdentifyOutlier(unittest.TestCase):
    def test_identify_outlier(self):      
        pq_data = load_pq_data()
        test_obj = identify_outlier(pq_data, group_var = "MetricDate", metric = "Collaboration_hours")
        # Check if the table is not empty
        self.assertFalse(test_obj.empty)
        # Check if the object is DataFrame
        self.assertTrue(isinstance(test_obj, pd.DataFrame))
        # Check if the columns has date values in the format 'YYYY-DD-MM'
        
if __name__ == '__main__':
    unittest.main()