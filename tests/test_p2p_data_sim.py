import unittest
import pandas as pd
from vivainsights import p2p_data_sim  # Replace with the actual module name

class TestP2PDataSimFunction(unittest.TestCase):
    def test_p2p_data_sim(self):
        # Test if the function returns a pandas DataFrame
        result_data = p2p_data_sim()
        self.assertIsInstance(result_data, pd.DataFrame)

        # Test if the DataFrame has the expected columns
        expected_columns = [
            'PrimaryCollaborator_PersonId', 'SecondaryCollaborator_PersonId',
            'PrimaryCollaborator_Organization', 'SecondaryCollaborator_Organization',
            'PrimaryCollaborator_LevelDesignation', 'SecondaryCollaborator_LevelDesignation',
            'PrimaryCollaborator_City', 'SecondaryCollaborator_City',
            'StrongTieScore'
        ]
        self.assertListEqual(list(result_data.columns), expected_columns)

        # Test if the DataFrame is not empty
        self.assertFalse(result_data.empty)

if __name__ == '__main__':
    unittest.main()
