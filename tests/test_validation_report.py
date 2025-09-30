import unittest
import os
import tempfile
import pandas as pd
from vivainsights import validation_report, load_pq_data


class TestValidationReport(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.pq_data = load_pq_data()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_validation_report_html_generation(self):
        """Test that validation_report generates an HTML file"""
        output_path = os.path.join(self.temp_dir, 'test_report.html')
        result = validation_report(self.pq_data, output_path=output_path)
        
        # Check that the function returns the output path
        self.assertEqual(result, output_path)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(output_path))
        
        # Check that the file has content
        self.assertGreater(os.path.getsize(output_path), 0)
    
    def test_validation_report_html_content(self):
        """Test that the HTML report contains expected sections"""
        output_path = os.path.join(self.temp_dir, 'test_report.html')
        validation_report(self.pq_data, output_path=output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key sections
        self.assertIn('Holiday Weeks Identification', content)
        self.assertIn('Non-Knowledge Workers Identification', content)
        self.assertIn('Collaboration Outliers', content)
        self.assertIn('HR Attributes Review', content)
        
        # Check that HTML structure is valid
        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('<html', content)
        self.assertIn('</html>', content)
    
    def test_validation_report_with_custom_hrvar(self):
        """Test validation_report with custom HR variables"""
        output_path = os.path.join(self.temp_dir, 'test_report_custom.html')
        result = validation_report(
            self.pq_data, 
            output_path=output_path,
            hrvar=['Organization', 'LevelDesignation', 'SupervisorIndicator']
        )
        
        # Check that the file was created
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that custom HR variables are in the report
        self.assertIn('Organization', content)
        self.assertIn('LevelDesignation', content)
        self.assertIn('SupervisorIndicator', content)
    
    def test_validation_report_print_only(self):
        """Test validation_report with print_only mode"""
        result = validation_report(self.pq_data, return_type='print_only')
        
        # Check that print_only returns None
        self.assertIsNone(result)
    
    def test_validation_report_with_single_hrvar_string(self):
        """Test that hrvar can be passed as a string"""
        output_path = os.path.join(self.temp_dir, 'test_report_string.html')
        result = validation_report(
            self.pq_data,
            output_path=output_path,
            hrvar='Organization'
        )
        
        # Check that the file was created
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that the HR variable is in the report
        self.assertIn('Organization', content)
    
    def test_validation_report_contains_plot(self):
        """Test that the report contains embedded plots"""
        output_path = os.path.join(self.temp_dir, 'test_report_plot.html')
        validation_report(self.pq_data, output_path=output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for base64 encoded image data
        self.assertIn('data:image/png;base64,', content)
    
    def test_validation_report_contains_metadata(self):
        """Test that the report contains dataset metadata"""
        output_path = os.path.join(self.temp_dir, 'test_report_metadata.html')
        validation_report(self.pq_data, output_path=output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for metadata fields
        self.assertIn('Total Records', content)
        self.assertIn('Unique Employees', content)
        self.assertIn('Date Range', content)
        self.assertIn('Report Generated', content)


if __name__ == '__main__':
    unittest.main()
