import unittest
import matplotlib.pyplot as plt
from  vivainsights.hrvar_count import hrvar_count_viz,hrvar_count_calc,hrvar_count_all
from vivainsights.pq_data import load_pq_data
import tracemalloc
import gc
import pandas as pd

def returnfig():
    fig = plt.figure()
    return fig

class TestHrVarCount(unittest.TestCase):
    def test_hrvar_count_viz(self):
        tracemalloc.start()        
        pq_data = load_pq_data()        
        fig = hrvar_count_viz(data=pq_data,hrvar = "LevelDesignation")
        del pq_data
        gc.collect()
        tracemalloc.stop()
        # Check if the image object is correct
        self.assertIsInstance(fig, plt.Figure)     
    
    def test_hrvar_count_calc(self):
        pq_data = load_pq_data()  
        test_obj=hrvar_count_calc(pq_data, hrvar="LevelDesignation")
        # Check if the table is not empty
        self.assertFalse(test_obj.empty)
        # Check if the DataFrame has the correct columns
        expected_columns = ["LevelDesignation", "n"]
        self.assertListEqual(list(test_obj.columns), expected_columns)

    def test_hrvar_count_all_default(self):
        """Test hrvar_count_all with default parameters (dynamic HR detection via extract_hr)"""
        pq_data = load_pq_data()
        result = hrvar_count_all(pq_data)
        
        # Check if the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check if the DataFrame has the correct columns
        expected_columns = ['hrvar', 'distinct_values', 'missing_count', 'missing_percentage']
        self.assertListEqual(list(result.columns), expected_columns)
        
        # Check if the DataFrame is not empty (extract_hr should find at least some HR variables)
        self.assertFalse(result.empty)
        
        # Check that all returned hrvars are actual columns in the data
        result_hrvars = result['hrvar'].tolist()
        for var in result_hrvars:
            self.assertIn(var, pq_data.columns)

    def test_hrvar_count_all_with_max_unique(self):
        """Test hrvar_count_all with custom max_unique parameter"""
        pq_data = load_pq_data()
        
        # Test with a lower max_unique threshold
        result_low = hrvar_count_all(pq_data, max_unique=10)
        
        # Test with a higher max_unique threshold
        result_high = hrvar_count_all(pq_data, max_unique=100)
        
        # Check if the results are DataFrames
        self.assertIsInstance(result_low, pd.DataFrame)
        self.assertIsInstance(result_high, pd.DataFrame)
        
        # Higher max_unique should generally find equal or more HR variables
        # (not strictly guaranteed, but typically true)
        self.assertGreaterEqual(len(result_high), len(result_low))

    def test_hrvar_count_all_custom(self):
        """Test hrvar_count_all with custom HR variables"""
        pq_data = load_pq_data()
        custom_vars = ['Organization', 'FunctionType']
        result = hrvar_count_all(pq_data, hrvar_list=custom_vars)
        
        # Check if the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check if only the specified variables are included
        result_hrvars = result['hrvar'].tolist()
        self.assertEqual(len(result_hrvars), 2)
        self.assertIn('Organization', result_hrvars)
        self.assertIn('FunctionType', result_hrvars)

    def test_hrvar_count_all_invalid_vars(self):
        """Test hrvar_count_all with invalid HR variables"""
        pq_data = load_pq_data()
        invalid_vars = ['NonExistentVar1', 'NonExistentVar2']
        
        # Should raise ValueError when no valid variables are found
        with self.assertRaises(ValueError):
            hrvar_count_all(pq_data, hrvar_list=invalid_vars)

    def test_hrvar_count_all_data_types(self):
        """Test that hrvar_count_all returns correct data types"""
        pq_data = load_pq_data()
        result = hrvar_count_all(pq_data)
        
        # Check data types
        self.assertTrue(result['hrvar'].dtype == 'object')  # string
        self.assertTrue(result['distinct_values'].dtype in ['int64', 'int32'])  # integer
        self.assertTrue(result['missing_count'].dtype in ['int64', 'int32'])  # integer
        self.assertTrue(result['missing_percentage'].dtype in ['float64', 'float32'])  # float

if __name__ == '__main__':
    unittest.main()