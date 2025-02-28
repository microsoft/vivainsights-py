import unittest
import matplotlib.pyplot as plt
from vivainsights.create_bubble import create_bubble
from vivainsights.pq_data import load_pq_data
import tracemalloc
import gc
import pandas as pd
import seaborn as sns

def returnfig():
    fig = plt.figure()
    return fig

class TestCreateBubble(unittest.TestCase):
    def test_create_bubble_plot(self):
        # Test that a plot is returned
        tracemalloc.start()
        pq_data = load_pq_data()
        fig = create_bubble(data=pq_data, metric_x='Emails_sent', metric_y='Collaboration_hours', hrvar='Organization')
        
        # garbage collection
        del pq_data
        gc.collect()
        
        tracemalloc.stop()
        
        # Check if fig is either a Matplotlib Figure or a Seaborn plot
        self.assertTrue(
            isinstance(fig, plt.Figure) or isinstance(fig, sns.axisgrid.FacetGrid),
            "Returned object is neither a Matplotlib Figure nor a Seaborn plot."
        )
    
    def test_create_bubble_table(self):
        # Test if create_bubble returns a DataFrame for table output
        pq_data = load_pq_data()
        table = create_bubble(data=pq_data, metric_x='Emails_sent', metric_y='Collaboration_hours', hrvar='Organization', return_type='table')
        self.assertIsInstance(table, pd.DataFrame)
    
    def test_create_bubble_no_hrvar_returns_plot(self):
        # Test that a plot is returned when hrvar is None
        tracemalloc.start()
        pq_data = load_pq_data()
        fig = create_bubble(data=pq_data, metric_x='Emails_sent', metric_y='Collaboration_hours', hrvar=None, return_type='plot')
        
        # garbage collection
        del pq_data
        gc.collect()
        
        tracemalloc.stop()
        self.assertIsInstance(fig, plt.Figure)
    
    def test_create_bubble_invalid_return_type(self):
        # Test that an invalid return_type raises a ValueError
        pq_data = load_pq_data()
        with self.assertRaises(ValueError):
            create_bubble(data=pq_data, metric_x='Emails_sent', metric_y='Collaboration_hours', hrvar='Organization', return_type='invalid_type')

if __name__ == '__main__':
    unittest.main()
