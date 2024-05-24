import pandas as pd
import unittest
from vivainsights.create_boxplot import create_boxplot_viz
from vivainsights.create_boxplot import create_boxplot_calc
from vivainsights.create_boxplot import create_boxplot
from vivainsights.pq_data import load_pq_data
import matplotlib.pyplot as plt
import tracemalloc
import gc


class TestCreateBoxplotViz(unittest.TestCase):
    def test_create_boxplot_viz(self):
        # Load sample data
        pq_data = load_pq_data()
        
        # Create a box plot of the emails sent grouped by organization
        output = create_boxplot_viz(pq_data, 'Emails_sent', 'Organization', mingroup=1)
        
        # Check that the output is a matplotlib.figure.Figure object
        self.assertIsInstance(output, plt.Figure)



class TestCreateBoxplotCalc(unittest.TestCase):
    def test_create_boxplot_calc(self):
        # Load sample data
        pq_data = load_pq_data()
        
        # Calculate box plot data for the emails sent metric grouped by organization
        output = create_boxplot_calc(pq_data, 'Emails_sent', 'Organization', mingroup=1)
        
        # Check that the output is a pandas DataFrame
        self.assertIsInstance(output, pd.DataFrame)
        
        # Check that the DataFrame has the correct columns
        self.assertListEqual(output.columns.tolist(), ['PersonId', 'group', 'Emails_sent', 'Employee_Count'])
        


class TestCreateBoxplot(unittest.TestCase):
    def test_create_boxplot_data(self):
        # Load sample data
        pq_data = load_pq_data()
        
        # Create a box plot of the emails sent grouped by organization
        output = create_boxplot(pq_data, 'Emails_sent', 'Organization', mingroup=1, return_type='data')
        
        # Check that the output is a pandas DataFrame
        self.assertIsInstance(output, pd.DataFrame)
        
        # Check that the DataFrame has the correct columns
        self.assertListEqual(output.columns.tolist(), ['PersonId', 'group', 'Emails_sent', 'Employee_Count'])

    def test_create_boxplot_plot(self):
        # Load sample data
        pq_data = load_pq_data()
        
        # Create a box plot of the emails sent grouped by organization
        output = create_boxplot(pq_data, 'Emails_sent', 'Organization', mingroup=1, return_type='plot')
        
        # Check that the output is a matplotlib.figure.Figure object
        self.assertIsInstance(output, plt.Figure)

    def test_create_boxplot_table(self):
        #load sample data
        pq_data = load_pq_data()

        # Create a box plot of the emails sent grouped by organization
        output = create_boxplot(pq_data, 'Emails_sent', 'Organization', mingroup=1, return_type='table')

        # Check that the output is a pandas DataFrame
        self.assertIsInstance(output, pd.DataFrame)

        # Check that the DataFrame has the correct columns
        self.assertListEqual(output.columns.tolist(), ['index','group', 'mean', 'median', 'sd', 'min', 'max', 'n'])

    def test_create_boxplot_no_hrvar_returns_plot(self):
        # Test that a plot is returned when hrvar is None        
        tracemalloc.start()
        pq_data = load_pq_data()
        # Create a box plot of the emails sent with no HR variable
        output = create_boxplot(
            data = pq_data,
            metric = 'Emails_sent',
            hrvar=None, 
            return_type='plot'
            )
        
        # garbage collection
        del pq_data
        gc.collect()
        
        # Check that the output is a matplotlib.figure.Figure object
        self.assertIsInstance(output, plt.Figure)
        
if __name__ == '__main__':
    unittest.main()
        


