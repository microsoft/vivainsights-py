import pandas as pd
import unittest
from vivainsights.create_trend import create_trend_viz
from vivainsights.pq_data import load_pq_data
from vivainsights.create_trend import create_trend_calc
from vivainsights.create_trend import create_trend
import matplotlib.pyplot as plt

class TestCreateTrend(unittest.TestCase):
    def setUp(self):
        # Load sample data
        self.pq_data = load_pq_data()
        
    def test_create_trend(self):
        # Test create_trend with default parameters
        output = create_trend(data = self.pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation")
        
        # Check that the output is a matplotlib Figure object
        self.assertIsInstance(output, plt.Figure)
        
    def test_create_trend_table(self):
        # Test create_trend with return_type = "table"
        output = create_trend(data = self.pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation", return_type = "table")
        
        # Check that the output is a pandas DataFrame
        self.assertIsInstance(output, pd.DataFrame)
       

class TestCreateTrendCalc(unittest.TestCase):
    def setUp(self):
        # Load sample data
        self.pq_data = load_pq_data()
        
    def test_create_trend_calc(self):
        # Test create_trend_calc with default parameters
        output = create_trend_calc(data = self.pq_data, metric = 'Collaboration_hours', hrvar = 'Organization', mingroup = 5, date_column = 'MetricDate', date_format = '%Y-%m-%d')
        
        # Check that the output is a pandas DataFrame
        self.assertIsInstance(output, pd.DataFrame)
        
        # Check that the output has the correct columns
        expected_columns = ['MetricDate', 'group', 'Employee_Count', 'Collaboration_hours']
        self.assertListEqual(list(output.columns), expected_columns)
        
        # Check that the output has the correct number of rows
        expected_rows = 245
        self.assertEqual(len(output), expected_rows)


class TestCreateTrendViz(unittest.TestCase):
    def setUp(self):
        # Load sample data
        self.pq_data = load_pq_data()
        
    def test_create_trend_viz(self):
        # Test create_trend_viz with default parameters
        output = output = create_trend_viz(data=self.pq_data, metric="Collaboration_hours", hrvar="LevelDesignation", palette="Blues", mingroup=2, legend_title="Legend", date_column="MetricDate", date_format="%Y-%m-%d")
        
        # Check that the figure has the expected number of subplots
        assert len(output.axes) == 2

        # Check that the title text is correct
        assert output.axes[0].texts[0].get_text() == "Collaboration hours Hotspots"

        # Check that the legend title is correct
        assert output.axes[1].get_ylabel() == "Legend"
        
if __name__ == '__main__':
    unittest.main()