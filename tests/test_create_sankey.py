import pandas as pd
import unittest
from vivainsights.create_sankey import create_sankey
from vivainsights.pq_data import load_pq_data

class TestCreateSankey(unittest.TestCase):
    def setUp(self):
        # Load sample data
        self.pq_data = load_pq_data()
        
    def test_create_sankey(self):
        sum_tb = self.pq_data.groupby(['Organization', 'LevelDesignation'])['PersonId'].nunique().reset_index(name='n')
        # Test create_sankey with default parameters
        try:    
            output = create_sankey(data = sum_tb, var1 = 'Organization', var2 = 'LevelDesignation')
        except Exception as e:
            self.fail(f"create_sankey raised an exception: {e}")
        
if __name__ == '__main__':
    unittest.main()