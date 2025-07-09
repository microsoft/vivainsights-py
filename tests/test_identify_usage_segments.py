import unittest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from vivainsights.identify_usage_segments import identify_usage_segments


class TestIdentifyUsageSegments(unittest.TestCase):
    
    def setUp(self):
        # Create sample test data
        np.random.seed(42)  # For reproducible tests
        self.test_data = pd.DataFrame({
            'PersonId': ['P1', 'P1', 'P1', 'P2', 'P2', 'P2'] * 10,
            'MetricDate': pd.date_range('2023-01-01', periods=60, freq='W'),
            'test_metric': np.random.randint(0, 20, 60)
        })
    
    def test_identify_usage_segments_12w_data(self):
        """Test 12w version returns data correctly."""
        result = identify_usage_segments(
            self.test_data, 
            metric='test_metric', 
            version='12w', 
            return_type='data'
        )
        
        # Check that result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check that UsageSegments_12w column is present
        self.assertIn('UsageSegments_12w', result.columns)
        
        # Check that all expected segments are present
        expected_segments = ["Power User", "Habitual User", "Novice User", "Low User", "Non-user"]
        actual_segments = result['UsageSegments_12w'].dropna().unique()
        self.assertTrue(all(segment in expected_segments for segment in actual_segments))
    
    def test_identify_usage_segments_4w_data(self):
        """Test 4w version returns data correctly."""
        result = identify_usage_segments(
            self.test_data, 
            metric='test_metric', 
            version='4w', 
            return_type='data'
        )
        
        # Check that result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check that UsageSegments_4w column is present
        self.assertIn('UsageSegments_4w', result.columns)
    
    def test_identify_usage_segments_custom_data(self):
        """Test custom parameters version returns data correctly."""
        result = identify_usage_segments(
            self.test_data, 
            metric='test_metric', 
            version=None,
            threshold=2,
            width=3,
            max_window=8,
            power_thres=10,
            return_type='data'
        )
        
        # Check that result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check that UsageSegments column is present (not versioned)
        self.assertIn('UsageSegments', result.columns)
        
        # Check that custom rolling average column is present
        self.assertIn('target_metric_l8w', result.columns)
    
    def test_identify_usage_segments_table_12w(self):
        """Test table return type for 12w version."""
        result = identify_usage_segments(
            self.test_data, 
            metric='test_metric', 
            version='12w', 
            return_type='table'
        )
        
        # Check that result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check that columns are the expected usage segments
        expected_columns = ["Non-user", "Low User", "Novice User", "Habitual User", "Power User"]
        self.assertListEqual(list(result.columns), expected_columns)
        
        # Check that index is MetricDate
        self.assertTrue(all(isinstance(idx, pd.Timestamp) for idx in result.index))
    
    def test_identify_usage_segments_table_custom(self):
        """Test table return type for custom parameters."""
        result = identify_usage_segments(
            self.test_data, 
            metric='test_metric', 
            version=None,
            threshold=2,
            width=3,
            max_window=8,
            power_thres=10,
            return_type='table'
        )
        
        # Check that result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check that columns are the expected usage segments
        expected_columns = ["Non-user", "Low User", "Novice User", "Habitual User", "Power User"]
        self.assertListEqual(list(result.columns), expected_columns)
    
    def test_identify_usage_segments_plot_12w(self):
        """Test plot return type for 12w version."""
        result = identify_usage_segments(
            self.test_data, 
            metric='test_metric', 
            version='12w', 
            return_type='plot'
        )
        
        # Check that result is a matplotlib Figure
        self.assertIsInstance(result, plt.Figure)
    
    def test_identify_usage_segments_plot_custom(self):
        """Test plot return type for custom parameters."""
        result = identify_usage_segments(
            self.test_data, 
            metric='test_metric', 
            version=None,
            threshold=2,
            width=3,
            max_window=8,
            power_thres=10,
            return_type='plot'
        )
        
        # Check that result is a matplotlib Figure
        self.assertIsInstance(result, plt.Figure)
    
    def test_validation_missing_custom_params(self):
        """Test that validation catches missing custom parameters."""
        with self.assertRaises(ValueError) as context:
            identify_usage_segments(
                self.test_data, 
                metric='test_metric', 
                version=None,
                threshold=2  # Missing other parameters
            )
        
        self.assertIn("threshold, width, max_window, and power_thres must be provided", str(context.exception))
    
    def test_validation_invalid_version(self):
        """Test that validation catches invalid version."""
        with self.assertRaises(ValueError) as context:
            identify_usage_segments(
                self.test_data, 
                metric='test_metric', 
                version='invalid'
            )
        
        self.assertIn("version must be '12w', '4w', or None", str(context.exception))
    
    def test_validation_invalid_return_type(self):
        """Test that validation catches invalid return_type."""
        with self.assertRaises(ValueError) as context:
            identify_usage_segments(
                self.test_data, 
                metric='test_metric', 
                return_type='invalid'
            )
        
        self.assertIn("return_type must be 'data', 'plot', or 'table'", str(context.exception))
    
    def test_validation_no_metric(self):
        """Test that validation catches missing metric parameters."""
        with self.assertRaises(ValueError) as context:
            identify_usage_segments(self.test_data)
        
        self.assertIn("Please provide either a metric or a metric_str", str(context.exception))


if __name__ == '__main__':
    unittest.main()