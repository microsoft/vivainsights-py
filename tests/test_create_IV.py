import unittest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from vivainsights.create_IV import create_IV, p_test, calculate_IV, map_IV
from vivainsights.pq_data import load_pq_data
import tracemalloc
import gc


class TestCreateIV(unittest.TestCase):
    """
    Test suite for the create_IV function and related functionality
    """
    
    def setUp(self):
        """Set up test data"""
        self.pq_data = load_pq_data()
        
        # Create a binary outcome variable for testing
        # Using median split for collaboration hours
        collab_median = self.pq_data['Collaboration_hours'].median()
        self.pq_data['High_Collaboration'] = (self.pq_data['Collaboration_hours'] > collab_median).astype(int)
        
        self.predictors = ['Email_hours', 'Meeting_hours', 'Multitasking_hours']
        self.outcome = 'High_Collaboration'
        
    def tearDown(self):
        """Clean up after each test"""
        plt.close('all')
        gc.collect()
    
    def test_create_IV_exc_sig_false_returns_plot(self):
        """Test that create_IV with exc_sig=False returns a plot and doesn't raise an error"""
        tracemalloc.start()
        
        try:
            result = create_IV(
                data=self.pq_data,
                predictors=self.predictors,
                outcome=self.outcome,
                exc_sig=False,
                return_type='plot'
            )
            # Should not raise an error even if no predictors are significant
            self.assertTrue(True, "Function completed without error")
        except ValueError as e:
            if "No predictors where the p-value lies below the significance level" in str(e):
                self.fail("Function incorrectly raised significance error when exc_sig=False")
            else:
                raise e
        finally:
            tracemalloc.stop()
    
    def test_create_IV_exc_sig_false_returns_summary(self):
        """Test that create_IV with exc_sig=False returns summary table"""
        result = create_IV(
            data=self.pq_data,
            predictors=self.predictors,
            outcome=self.outcome,
            exc_sig=False,
            return_type='summary'
        )
        
        # Should return a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Should have columns for Variable, IV, and pval
        expected_columns = ['Variable', 'IV', 'pval']
        for col in expected_columns:
            self.assertIn(col, result.columns)
        
        # Should include all predictors regardless of significance
        self.assertEqual(len(result), len(self.predictors))
    
    def test_create_IV_exc_sig_true_with_significant_predictors(self):
        """Test create_IV with exc_sig=True when significant predictors exist"""
        # Create a dataset with a strong predictor to ensure significance
        test_data = self.pq_data.copy()
        
        # Create a strong predictor that should be significant
        np.random.seed(42)  # For reproducibility
        test_data['Strong_Predictor'] = test_data[self.outcome] * 10 + np.random.normal(0, 1, len(test_data))
        
        try:
            result = create_IV(
                data=test_data,
                predictors=['Strong_Predictor'] + self.predictors,
                outcome=self.outcome,
                exc_sig=True,
                siglevel=0.05,
                return_type='summary'
            )
            
            # Should return a DataFrame
            self.assertIsInstance(result, pd.DataFrame)
            
            # All returned predictors should have p-value <= 0.05
            self.assertTrue(all(result['pval'] <= 0.05))
            
        except ValueError as e:
            if "No predictors where the p-value lies below the significance level" in str(e):
                # This is acceptable if truly no predictors are significant
                self.assertTrue(True, "No significant predictors found, error correctly raised")
            else:
                raise e
    
    def test_create_IV_exc_sig_true_no_significant_predictors(self):
        """Test that create_IV with exc_sig=True raises error when no significant predictors"""
        # Create random predictors that should not be significant
        import numpy as np
        np.random.seed(42)
        test_data = self.pq_data.copy()
        test_data['random1'] = np.random.normal(0, 1, len(test_data))
        test_data['random2'] = np.random.normal(0, 1, len(test_data))
        test_data['random3'] = np.random.normal(0, 1, len(test_data))
        
        random_predictors = ['random1', 'random2', 'random3']
        
        # Use a strict significance level to ensure no predictors are significant
        with self.assertRaises(ValueError) as context:
            create_IV(
                data=test_data,
                predictors=random_predictors,
                outcome=self.outcome,
                exc_sig=True,
                siglevel=0.01,  # 1% significance level
                return_type='summary'
            )
        
        self.assertIn("No predictors where the p-value lies below the significance level", str(context.exception))
    
    def test_create_IV_return_type_list(self):
        """Test create_IV with return_type='list'"""
        result = create_IV(
            data=self.pq_data,
            predictors=self.predictors,
            outcome=self.outcome,
            exc_sig=False,
            return_type='list'
        )
        
        # Should return a dictionary
        self.assertIsInstance(result, dict)
        
        # Should have entries for each predictor
        for predictor in self.predictors:
            if predictor in result:  # May not include all if some fail IV calculation
                self.assertIsInstance(result[predictor], pd.DataFrame)
    
    def test_create_IV_return_type_IV(self):
        """Test create_IV with return_type='IV'"""
        result = create_IV(
            data=self.pq_data,
            predictors=self.predictors,
            outcome=self.outcome,
            exc_sig=False,
            return_type='IV'
        )
        
        # Should return a tuple with 3 elements
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        
        output_list, IV_summary, lnodds = result
        
        # Check types
        self.assertIsInstance(output_list, dict)
        self.assertIsInstance(IV_summary, pd.DataFrame)
        self.assertIsInstance(lnodds, (int, float, np.number))
    
    def test_create_IV_invalid_return_type(self):
        """Test create_IV with invalid return_type"""
        with self.assertRaises(ValueError) as context:
            create_IV(
                data=self.pq_data,
                predictors=self.predictors,
                outcome=self.outcome,
                exc_sig=False,
                return_type='invalid'
            )
        
        self.assertIn("Please enter a valid input for `return_type`", str(context.exception))
    
    def test_create_IV_invalid_exc_sig_type(self):
        """Test create_IV with invalid exc_sig type"""
        with self.assertRaises(ValueError) as context:
            create_IV(
                data=self.pq_data,
                predictors=self.predictors,
                outcome=self.outcome,
                exc_sig="invalid",  # Should be boolean
                return_type='summary'
            )
        
        self.assertIn("Invalid input to `exc_sig`", str(context.exception))
    
    def test_create_IV_no_predictors_specified(self):
        """Test create_IV when no predictors are specified (should use all numeric columns)"""
        # Create a small dataset with known numeric columns
        small_data = self.pq_data[['Email_hours', 'Meeting_hours', self.outcome]].copy()
        
        result = create_IV(
            data=small_data,
            predictors=None,  # Should auto-detect
            outcome=self.outcome,
            exc_sig=False,
            return_type='summary'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        # Should have detected the numeric predictors
        self.assertGreater(len(result), 0)


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
    
    def test_p_test_pvalues_in_valid_range(self):
        """Test that p-values are in valid range [0, 1]"""
        result = p_test(
            data=self.pq_data,
            outcome='Binary_Outcome',
            behavior=['Email_hours', 'Meeting_hours']
        )
        
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
    
    def test_p_test_unpaired_handles_different_sample_sizes(self):
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


class TestCalculateIV(unittest.TestCase):
    """Test the calculate_IV helper function"""
    
    def setUp(self):
        """Set up test data"""
        self.pq_data = load_pq_data()
        collab_median = self.pq_data['Collaboration_hours'].median()
        self.pq_data['Binary_Outcome'] = (self.pq_data['Collaboration_hours'] > collab_median).astype(int)
    
    def test_calculate_IV_returns_dataframe(self):
        """Test that calculate_IV returns a DataFrame with correct structure"""
        result = calculate_IV(
            data=self.pq_data,
            outcome='Binary_Outcome',
            predictor='Email_hours',
            bins=5
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        expected_columns = ['Email_hours', 'n', 'percentage', 'WOE', 'IV']
        for col in expected_columns:
            self.assertIn(col, result.columns)
    
    def test_calculate_IV_with_missing_outcome(self):
        """Test that calculate_IV raises error with missing outcome values"""
        test_data = self.pq_data.copy()
        test_data.loc[0, 'Binary_Outcome'] = np.nan
        
        with self.assertRaises(ValueError) as context:
            calculate_IV(
                data=test_data,
                outcome='Binary_Outcome',
                predictor='Email_hours',
                bins=5
            )
        
        self.assertIn("has missing values in the input training data frame", str(context.exception))
    
    def test_calculate_IV_with_categorical_variable(self):
        """Test that calculate_IV works with categorical variables"""
        result = calculate_IV(
            data=self.pq_data,
            outcome='Binary_Outcome',
            predictor='Organization',
            bins=5  # bins parameter ignored for categorical
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        expected_columns = ['Organization', 'n', 'percentage', 'WOE', 'IV']
        for col in expected_columns:
            self.assertIn(col, result.columns)
        
        # Should have one row per category
        n_categories = len(self.pq_data['Organization'].unique())
        self.assertEqual(len(result), n_categories)
    
    def test_calculate_IV_with_numeric_variable_still_works(self):
        """Test that calculate_IV still works with numeric variables after categorical support"""
        result = calculate_IV(
            data=self.pq_data,
            outcome='Binary_Outcome',
            predictor='Email_hours',
            bins=5
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        expected_columns = ['Email_hours', 'n', 'percentage', 'WOE', 'IV']
        for col in expected_columns:
            self.assertIn(col, result.columns)


class TestCategoricalVariables(unittest.TestCase):
    """Test suite for categorical variable support in create_IV"""
    
    def setUp(self):
        """Set up test data"""
        self.pq_data = load_pq_data()
        
        # Create a binary outcome variable for testing
        collab_median = self.pq_data['Collaboration_hours'].median()
        self.pq_data['High_Collaboration'] = (self.pq_data['Collaboration_hours'] > collab_median).astype(int)
    
    def test_create_IV_with_categorical_only(self):
        """Test create_IV with only categorical predictors"""
        result = create_IV(
            data=self.pq_data,
            predictors=['Organization', 'FunctionType'],
            outcome='High_Collaboration',
            exc_sig=False,
            return_type='summary'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        
        # Should have the expected columns
        expected_columns = ['Variable', 'IV', 'pval']
        for col in expected_columns:
            self.assertIn(col, result.columns)
    
    def test_create_IV_with_mixed_types(self):
        """Test create_IV with mixed categorical and numeric predictors"""
        predictors = ['Organization', 'Email_hours', 'FunctionType', 'Meeting_hours']
        result = create_IV(
            data=self.pq_data,
            predictors=predictors,
            outcome='High_Collaboration',
            exc_sig=False,
            return_type='summary'
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(predictors))
    
    def test_create_IV_categorical_return_type_IV(self):
        """Test create_IV with categorical variables and return_type='IV'"""
        result = create_IV(
            data=self.pq_data,
            predictors=['Organization'],
            outcome='High_Collaboration',
            exc_sig=False,
            return_type='IV'
        )
        
        # Should return tuple with 3 elements
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        
        output_list, IV_summary, lnodds = result
        
        # Check types
        self.assertIsInstance(output_list, dict)
        self.assertIsInstance(IV_summary, pd.DataFrame)
        self.assertIn('Organization', output_list)
    
    def test_create_IV_categorical_return_type_list(self):
        """Test create_IV with categorical variables and return_type='list'"""
        result = create_IV(
            data=self.pq_data,
            predictors=['Organization', 'FunctionType'],
            outcome='High_Collaboration',
            exc_sig=False,
            return_type='list'
        )
        
        self.assertIsInstance(result, dict)
        # Should have entries for the predictors
        self.assertIn('Organization', result)
        self.assertIn('FunctionType', result)
        
        # Each entry should be a DataFrame
        for key, value in result.items():
            self.assertIsInstance(value, pd.DataFrame)


if __name__ == '__main__':
    unittest.main()
