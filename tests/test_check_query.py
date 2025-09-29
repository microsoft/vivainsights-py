import unittest
from vivainsights import check_query
from vivainsights.pq_data import load_pq_data
import pandas as pd
import re


class TestCheckQuery(unittest.TestCase):

    def setUp(self):
        """Set up test data for all tests."""
        self.pq_data = load_pq_data()

    def test_check_query_basic_functionality(self):
        """Test basic functionality of check_query with message return type."""
        # Should run without error and return None for message type
        result = check_query(self.pq_data)
        self.assertIsNone(result)

    def test_check_query_text_return_type(self):
        """Test check_query with text return type."""
        result = check_query(self.pq_data, return_type="text")
        
        # Should return a string
        self.assertIsInstance(result, str)
        
        # Should not be empty
        self.assertTrue(len(result) > 0)
        
        # Should contain key information
        self.assertIn("employees in this dataset", result)
        self.assertIn("Data from", result)
        self.assertIn("HR attributes in the data", result)

    def test_check_query_employee_count(self):
        """Test that employee count is correctly reported."""
        result = check_query(self.pq_data, return_type="text")
        
        # Check that employee count matches actual unique PersonId count
        actual_count = self.pq_data['PersonId'].nunique()
        expected_pattern = f"There are {actual_count} employees in this dataset"
        self.assertIn(expected_pattern, result)

    def test_check_query_date_range(self):
        """Test that date range is correctly reported."""
        result = check_query(self.pq_data, return_type="text")
        
        # Should contain date range information
        self.assertIn("Data from", result)
        
        # Should contain valid date format (YYYY-MM-DD)
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        dates_found = re.findall(date_pattern, result)
        self.assertGreaterEqual(len(dates_found), 2)  # Should find at least start and end dates
        
        # Validate that dates can be parsed
        for date_str in dates_found:
            try:
                pd.to_datetime(date_str)
            except ValueError:
                self.fail(f"Invalid date format found: {date_str}")

    def test_check_query_hr_attributes(self):
        """Test that HR attributes are correctly identified and reported."""
        result = check_query(self.pq_data, return_type="text")
        
        # Should contain HR attributes information
        self.assertIn("HR attributes in the data", result)
        
        # Should not include PersonId or MetricDate in HR attributes
        self.assertNotIn("`PersonId`", result)
        self.assertNotIn("`MetricDate`", result)
        
        # Should include known HR attributes with backticks
        expected_hr_attributes = ['Organization', 'FunctionType', 'Level']
        for attr in expected_hr_attributes:
            if attr in self.pq_data.columns:
                self.assertIn(f"`{attr}`", result)

    def test_check_query_isactive_flag(self):
        """Test IsActive flag reporting."""
        result = check_query(self.pq_data, return_type="text")
        
        if "IsActive" not in self.pq_data.columns:
            self.assertIn("The `IsActive` flag is not present in the data", result)
        else:
            self.assertIn("active employees out of all in the dataset", result)

    def test_check_query_with_isactive_column(self):
        """Test check_query behavior when IsActive column is present."""
        # Create test data with IsActive column
        test_data = self.pq_data.copy()
        test_data['IsActive'] = True  # All employees active
        test_data.loc[test_data.index[:50], 'IsActive'] = False  # Set some as inactive
        
        result = check_query(test_data, return_type="text")
        
        # Should report active employee count
        self.assertIn("active employees out of all in the dataset", result)
        self.assertNotIn("The `IsActive` flag is not present", result)

    def test_check_query_invalid_input(self):
        """Test error handling for invalid inputs."""
        # Test with non-DataFrame input
        with self.assertRaises(ValueError) as context:
            check_query("not a dataframe")
        self.assertIn("not a pandas DataFrame", str(context.exception))

        # Test with DataFrame missing PersonId
        invalid_data = pd.DataFrame({'SomeColumn': [1, 2, 3]})
        with self.assertRaises(ValueError) as context:
            check_query(invalid_data)
        self.assertIn("no `PersonId` variable", str(context.exception))

        # Test with DataFrame missing MetricDate
        invalid_data = pd.DataFrame({'PersonId': [1, 2, 3]})
        with self.assertRaises(ValueError) as context:
            check_query(invalid_data)
        self.assertIn("no `MetricDate` variable", str(context.exception))

    def test_check_query_invalid_return_type(self):
        """Test error handling for invalid return_type."""
        with self.assertRaises(ValueError) as context:
            check_query(self.pq_data, return_type="invalid")
        self.assertIn("Please check inputs for `return_type`", str(context.exception))

    def test_check_query_output_format(self):
        """Test that the output format matches expected structure."""
        result = check_query(self.pq_data, return_type="text")
        
        # Split into lines for analysis
        lines = result.split('\n')
        
        # Should have multiple non-empty lines
        non_empty_lines = [line for line in lines if line.strip()]
        self.assertGreater(len(non_empty_lines), 3)
        
        # First line should be about employee count
        self.assertIn("employees in this dataset", lines[0])
        
        # Should contain proper formatting with empty lines between sections
        self.assertIn('', lines)  # Should have empty lines for spacing


if __name__ == '__main__':
    unittest.main()