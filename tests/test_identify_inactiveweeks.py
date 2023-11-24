import unittest
from  vivainsights.identify_inactiveweeks import identify_inactiveweeks
from vivainsights.pq_data import load_pq_data
import pandas as pd

class TestIdentifyInactiveWeeks(unittest.TestCase):
    def test_identify_inactiveweeks(self):       
        pq_data = load_pq_data()        
        
        test_obj = identify_inactiveweeks(pq_data, sd=2, return_type="data")
        # Check if the table is not empty
        self.assertFalse(test_obj.empty)
        # Check if the object is DataFrame
        self.assertTrue(isinstance(test_obj, pd.DataFrame))

        test_obj_data_dirty = identify_inactiveweeks(pq_data, sd=2, return_type="data_dirty")
        # Check if the table is not empty
        self.assertFalse(test_obj_data_dirty.empty)
        # Check if the object is DataFrame
        self.assertTrue(isinstance(test_obj_data_dirty, pd.DataFrame))
        
        test_obj_dirty_data = identify_inactiveweeks(pq_data, sd=2, return_type="dirty_data")
        # Check if the table is not empty
        self.assertFalse(test_obj_dirty_data.empty)
        # Check if the object is DataFrame
        self.assertTrue(isinstance(test_obj_dirty_data, pd.DataFrame))

        test_obj_data_cleaned = identify_inactiveweeks(pq_data, sd=2, return_type="data_cleaned")
        # Check if the table is not empty
        self.assertFalse(test_obj_data_cleaned.empty)
        # Check if the object is DataFrame
        self.assertTrue(isinstance(test_obj_data_cleaned, pd.DataFrame))

        test_obj_cleaned_data = identify_inactiveweeks(pq_data, sd=2, return_type="cleaned_data")
        # Check if the table is not empty
        self.assertFalse(test_obj_cleaned_data.empty)
        # Check if the object is DataFrame
        self.assertTrue(isinstance(test_obj_cleaned_data, pd.DataFrame))

        test_text = identify_inactiveweeks(pq_data, sd=2, return_type="text")
        # Check if the text is generated and not empty
        self.assertTrue(test_text)
        
        
if __name__ == '__main__':
    unittest.main()