import unittest
import matplotlib.pyplot as plt
from vivainsights.create_line import create_line_viz
from vivainsights.create_line import create_line_calc
from vivainsights.create_line import create_line
from vivainsights.pq_data import load_pq_data
import tracemalloc
import gc
import pandas as pd

def returnfig():
    fig = plt.figure()
    return fig

class TestCreateLine(unittest.TestCase):
    def test_create_line(self):
        # Test that a plot is returned
        tracemalloc.start()        
        pq_data = load_pq_data()        
        fig = create_line_viz(data = pq_data, metric='Emails_sent', hrvar='Organization')
        
        # garbage collection
        del pq_data
        gc.collect()
        
        tracemalloc.stop()
        self.assertIsInstance(fig, plt.Figure)
        
    def test_create_line_table(self):
        # Test if create_line returns a DataFrame for table output
        pq_data = load_pq_data() 
        table = create_line_calc(data=pq_data, metric="Emails_sent", hrvar="Organization", mingroup=5)
        self.assertIsInstance(table, pd.DataFrame)
        
    def test_create_line_no_hrvar_returns_plot(self):
        # Test that a plot is returned when hrvar is None        
        tracemalloc.start()
        pq_data = load_pq_data()         
        fig = create_line(
            data= pq_data,
            metric='Emails_sent',
            hrvar=None,
            mingroup=5,
            return_type='plot'
        )
        # garbage collection
        del pq_data
        gc.collect()
        
        tracemalloc.stop()
        self.assertIsInstance(fig, plt.Figure)

if __name__ == '__main__':
    unittest.main()
