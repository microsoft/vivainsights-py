import unittest
import pandas as pd
from vivainsights import totals_col  # Replace with the actual module name

class TestTotalsColFunction(unittest.TestCase):
    def test_totals_col(self):
        # Create a sample DataFrame for testing
        sample_data = pd.DataFrame({
            'Column1': [1, 2, 3],
            'Column2': ['A', 'B', 'C']
        })

        # Test if the function modifies the DataFrame correctly
        result_data = totals_col(sample_data)
        
        # Test if the new column is added
        self.assertIn('Total', result_data.columns)

        # Test if the values in the new column match the specified total_value
        self.assertTrue(all(result_data['Total'] == 'Total'))

if __name__ == '__main__':
    unittest.main()
