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
    
    def test_create_line_table(self):
        pq_data = load_pq_data()
        # Test if create_line returns a DataFrame for table output
        table = create_rank_calc(data=pq_data, metric="Emails_sent", hrvar=['Organization', 'FunctionType', 'LevelDesignation', 'SupervisorIndicator'], mingroup=5)
        self.assertIsInstance(table, pd.DataFrame)     

if __name__ == '__main__':
    unittest.main()