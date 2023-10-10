import pandas as pd
import unittest
from vivainsights.create_boxplot import create_boxplot_viz
from vivainsights.create_boxplot import create_boxplot_calc
from vivainsights.create_boxplot import create_boxplot
from vivainsights.pq_data import load_pq_data
import matplotlib.pyplot as plt


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

        
if __name__ == '__main__':
    unittest.main()
        


