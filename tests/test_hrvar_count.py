import unittest
import matplotlib.pyplot as plt
from  vivainsights.hrvar_count import hrvar_count_viz,hrvar_count_calc
from vivainsights.pq_data import load_pq_data
import tracemalloc
import gc

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

if __name__ == '__main__':
    unittest.main()