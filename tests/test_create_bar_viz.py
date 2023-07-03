import unittest
import matplotlib.pyplot as plt
from vivainsights.create_bar import create_bar_viz
from vivainsights.pq_data import load_pq_data
import tracemalloc
import gc

def returnfig():
    fig = plt.figure()
    return fig

class TestCreateBarViz(unittest.TestCase):
    def test_create_bar_viz(self):
        tracemalloc.start()        
        pq_data = load_pq_data()        
        fig = create_bar_viz(data = pq_data, metric='Emails_sent', hrvar='Organization')
        
        # garbage collection
        del pq_data
        gc.collect()
        
        tracemalloc.stop()
        self.assertIsInstance(fig, plt.Figure)     

if __name__ == '__main__':
    unittest.main()
