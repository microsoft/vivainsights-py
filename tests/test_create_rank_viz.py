import unittest
import matplotlib.pyplot as plt
from vivainsights.create_rank import create_rank_viz, create_rank_calc
from vivainsights.pq_data import load_pq_data
import tracemalloc
import gc
import pandas as pd

def returnfig():
    fig = plt.figure()
    return fig

class TestCreateRank(unittest.TestCase):
    def test_create_rank(self):
        tracemalloc.start()        
        pq_data = load_pq_data()        
        fig = create_rank_viz(data = pq_data,metric="Emails_sent", hrvar = ['Organization', 'FunctionType', 'LevelDesignation', 'SupervisorIndicator'],mingroup = 5)
        
        # garbage collection
        del pq_data
        gc.collect()
        
        tracemalloc.stop()
        self.assertIsInstance(fig, plt.Figure)
    
    def test_create_rank_table(self):
        pq_data = load_pq_data()
        # Test if create_rank returns a DataFrame for table output
        table = create_rank_calc(data=pq_data, metric="Emails_sent", hrvar=['Organization', 'FunctionType', 'LevelDesignation', 'SupervisorIndicator'], mingroup=5)
        self.assertIsInstance(table, pd.DataFrame)     
        
    def test_create_rank_calc_stats(self):
        pq_data = load_pq_data()
        # Test if create_rank_calc returns a data frame with columns 'sd', 'median', 'min', 'max' when stats = True
        table = create_rank_calc(
            data=pq_data,
            metric="Emails_sent",
            hrvar=['Organization', 'FunctionType', 'LevelDesignation', 'SupervisorIndicator'],
            mingroup=5,
            stats=True
            )
        
        # Check that the returned dataframe contains the required columns
        expected_columns = ['sd', 'median', 'min', 'max']
        for col in expected_columns:
            self.assertIn(col, table.columns)

        # Check that the values in the 'sd', 'median', 'min', 'max' columns are not null
        self.assertFalse(table[['sd', 'median', 'min', 'max']].isnull().values.any())        

if __name__ == '__main__':
    unittest.main()