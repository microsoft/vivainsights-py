import unittest
import pandas as pd
import os
from vivainsights import import_query 

class TestImportQueryFunction(unittest.TestCase):
    def setUp(self):
        # Create a temporary CSV file for testing
        self.test_csv_content = "Name,Age,Salary\nJohn,25,50000\nJane,30,60000"
        with open('test_file.csv', 'w') as temp_file:
            temp_file.write(self.test_csv_content)

    def tearDown(self):
        # Remove the temporary CSV file after testing
        try:
            os.remove('test_file.csv')
        except FileNotFoundError:
            pass

    def test_import_query_valid_file(self):
        # Test if the function successfully imports a valid CSV file
        result_df = import_query('test_file.csv')
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(result_df.shape, (2, 3))  # the CSV file has 2 rows and 3 columns

    def test_import_query_nonexistent_file(self):
        # Test if the function raises a ValueError for a nonexistent file
        with self.assertRaises(ValueError) as context:
            import_query('nonexistent_file.csv')
        self.assertEqual(str(context.exception), "input file does not exist")


if __name__ == '__main__':
    unittest.main()
