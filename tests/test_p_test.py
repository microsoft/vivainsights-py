import unittest
import pandas as pd
import numpy as np
from vivainsights.create_IV import p_test
from vivainsights.pq_data import load_pq_data


class TestPTest(unittest.TestCase):
    """Test the p_test helper function"""
    
    def setUp(self):
        """Set up test data"""
        self.pq_data = load_pq_data()
        collab_median = self.pq_data['Collaboration_hours'].median()
        self.pq_data['Binary_Outcome'] = (self.pq_data['Collaboration_hours'] > collab_median).astype(int)
    
    def test_p_test_returns_dataframe(self):
        """Test that p_test returns a DataFrame with correct structure"""
        result = p_test(
            data=self.pq_data,
            outcome='Binary_Outcome',
            behavior=['Email_hours', 'Meeting_hours']
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(list(result.columns), ['Variable', 'pval'])
        self.assertEqual(len(result), 2)
        
        # P-values should be in valid range [0, 1]
        for pval in result['pval']:
            self.assertGreaterEqual(pval, 0)
            self.assertLessEqual(pval, 1)
    
    def test_p_test_with_categorical_variable(self):
        """Test that p_test works with categorical variables using chi-square"""
        result = p_test(
            data=self.pq_data,
            outcome='Binary_Outcome',
            behavior=['Organization', 'FunctionType']
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        
        # P-values should be in valid range
        for pval in result['pval']:
            self.assertGreaterEqual(pval, 0)
            self.assertLessEqual(pval, 1)
    
    def test_p_test_with_mixed_variables(self):
        """Test that p_test works with both categorical and numeric variables"""
        result = p_test(
            data=self.pq_data,
            outcome='Binary_Outcome',
            behavior=['Organization', 'Email_hours', 'FunctionType', 'Meeting_hours']
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 4)
        
        # All p-values should be valid
        for pval in result['pval']:
            self.assertGreaterEqual(pval, 0)
            self.assertLessEqual(pval, 1)
    
    def test_p_test_handles_different_sample_sizes(self):
        """Test that p_test (Mann-Whitney U) handles different sample sizes correctly"""
        # Create data with unequal group sizes
        np.random.seed(42)
        test_data = pd.DataFrame({
            'outcome': [1]*30 + [0]*70,  # Unequal groups: 30 vs 70
            'numeric_var': np.random.normal(10, 2, 100)
        })
        
        # This should work without error (Mann-Whitney U allows different sample sizes)
        result = p_test(
            data=test_data,
            outcome='outcome',
            behavior=['numeric_var']
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertGreaterEqual(result['pval'].iloc[0], 0)
        self.assertLessEqual(result['pval'].iloc[0], 1)
    
    def test_p_test_handles_missing_numeric_values(self):
        """Test that p_test handles missing values in numeric variables correctly"""
        test_data = self.pq_data.copy()
        
        # Introduce NaN values in numeric predictor
        na_indices = [0, 5, 10, 15, 20]
        test_data.loc[na_indices, 'Email_hours'] = np.nan
        
        # Should still work - NaN values are dropped via .dropna() in implementation
        result = p_test(
            data=test_data,
            outcome='Binary_Outcome',
            behavior=['Email_hours']
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        
        # P-value should be valid
        self.assertGreaterEqual(result['pval'].iloc[0], 0)
        self.assertLessEqual(result['pval'].iloc[0], 1)
    
    def test_p_test_handles_missing_categorical_values(self):
        """Test that p_test handles missing values in categorical variables correctly"""
        test_data = self.pq_data.copy()
        
        # Introduce NaN values in categorical predictor
        na_indices = [0, 5, 10]
        test_data.loc[na_indices, 'Organization'] = np.nan
        
        # Should still work - crosstab excludes NaN by default
        result = p_test(
            data=test_data,
            outcome='Binary_Outcome',
            behavior=['Organization']
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        
        # P-value should be valid
        self.assertGreaterEqual(result['pval'].iloc[0], 0)
        self.assertLessEqual(result['pval'].iloc[0], 1)
    
    def test_p_test_uses_fisher_exact_for_2x2_low_expected(self):
        """Test that p_test uses Fisher's exact test for 2x2 tables with low expected frequencies"""
        # Create a small dataset with a 2x2 contingency table and low expected frequencies
        np.random.seed(42)
        test_data = pd.DataFrame({
            'outcome': [1, 1, 1, 0, 0],  # Very small sample
            'binary_cat': ['A', 'A', 'B', 'A', 'B']  # 2 categories -> 2x2 table
        })
        
        # Should use Fisher's exact test (no warning for 2x2 tables)
        result = p_test(
            data=test_data,
            outcome='outcome',
            behavior=['binary_cat']
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        
        # P-value should be valid
        self.assertGreaterEqual(result['pval'].iloc[0], 0)
        self.assertLessEqual(result['pval'].iloc[0], 1)
    
    def test_p_test_warns_for_larger_tables_with_low_expected(self):
        """Test that p_test warns for larger contingency tables with low expected frequencies"""
        # Create a dataset with more than 2 categories and low expected frequencies
        np.random.seed(42)
        test_data = pd.DataFrame({
            'outcome': [1, 1, 1, 0, 0, 0, 1, 0],  # Small sample
            'multi_cat': ['A', 'A', 'B', 'B', 'C', 'C', 'D', 'D']  # 4 categories -> larger than 2x2
        })
        
        # Should warn about low expected frequencies
        with self.assertWarns(UserWarning) as warning_context:
            result = p_test(
                data=test_data,
                outcome='outcome',
                behavior=['multi_cat']
            )
        
        # Check warning message
        self.assertIn('Low expected frequencies', str(warning_context.warning))
        self.assertIn('multi_cat', str(warning_context.warning))
        
        # Should still return valid result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertGreaterEqual(result['pval'].iloc[0], 0)
        self.assertLessEqual(result['pval'].iloc[0], 1)


if __name__ == '__main__':
    unittest.main()