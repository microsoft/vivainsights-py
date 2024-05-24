import unittest
import matplotlib.pyplot as plt
from vivainsights.create_bar import create_bar_viz
from vivainsights.create_bar import create_bar_calc
from vivainsights.create_bar import create_bar
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
        
    def test_create_bar_no_hrvar_returns_plot(self):
        # Test that a plot is returned when hrvar is None 
        tracemalloc.start()
        pq_data = load_pq_data()    
        fig = create_bar(
            data = pq_data,
            metric = 'Emails_sent',
            hrvar=None,
            return_type='plot'
            )
        # garbage collection
        del pq_data
        gc.collect()
        
        tracemalloc.stop()
        self.assertIsInstance(fig, plt.Figure)
        
        
class TestCreateBarCalc(unittest.TestCase):
    def test_create_bar_calc_stats(self):
        pq_data = load_pq_data()
        # Test if create_rank_calc returns a data frame with columns 'sd', 'median', 'min', 'max' when stats = True
        table = create_bar_calc(
            data=pq_data,
            metric="Emails_sent",
            hrvar='Organization',
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
