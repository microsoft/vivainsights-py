import unittest
import os
import vivainsights as vi
from vivainsights.pq_data import load_pq_data
from PIL import Image, ImageDraw
from vivainsights import export, display_plot



class TestExport(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = 'test_files'
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        # Remove the temporary directory and its contents
        for file_name in os.listdir(self.test_dir):
            file_path = os.path.join(self.test_dir, file_name)
            os.remove(file_path)
        os.rmdir(self.test_dir)

    def test_generate_csv(self):
        pq_data=load_pq_data()
        file_path = os.path.join(self.test_dir)
        export(pq_data,
           file_format='csv',
           path=file_path,
           timestamp=False)
        # Check if the file was created
        self.assertTrue(os.path.exists(file_path))
        
        file_path=file_path+'.csv'
        # Check if the file is not empty
        with open(file_path, 'r') as file:
            content = file.read()
            self.assertNotEqual(content, '')\
                
                
    def test_generate_png(self):
        file_path = os.path.join(self.test_dir)
        pq_data=load_pq_data()
        trend=vi.create_trend(data = pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation")
        export(trend,
           file_format='png',
           path=file_path,
           timestamp=False)
        # Check if the file was created
        self.assertTrue(os.path.exists(file_path))
        
        
    def test_generate_svg(self):
        file_path = os.path.join(self.test_dir)
        pq_data=load_pq_data()
        trend=vi.create_trend(data = pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation")
        export(trend,
           file_format='svg',
           path=file_path,
           timestamp=False)
        # Check if the file was created
        self.assertTrue(os.path.exists(file_path))        

    def test_generate_jpeg(self):
        file_path = os.path.join(self.test_dir)
        pq_data=load_pq_data()
        trend=vi.create_trend(data = pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation")
        export(trend,
           file_format='jpeg',
           path=file_path,
           timestamp=False)
        # Check if the file was created
        self.assertTrue(os.path.exists(file_path))  


    def test_generate_pdf(self):
        file_path = os.path.join(self.test_dir)
        pq_data=load_pq_data()
        trend=vi.create_trend(data = pq_data, metric = "Collaboration_hours", hrvar = "LevelDesignation")
        export(trend,
           file_format='pdf',
           path=file_path,
           timestamp=False)
        # Check if the file was created
        self.assertTrue(os.path.exists(file_path))  

    def test_auto_behavior_plot(self):
        # Test that auto behavior displays plots (we can't easily test display, so we test it doesn't raise an error)
        pq_data = load_pq_data()
        trend = vi.create_trend(data=pq_data, metric="Collaboration_hours", hrvar="LevelDesignation")
        try:
            # This should call display_plot() without error
            export(trend, file_format='auto')
            # If we get here without exception, the test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Auto behavior for plot objects failed: {e}")

    def test_auto_behavior_dataframe(self):
        # Test that auto behavior copies DataFrames to clipboard
        # Note: We can't easily test clipboard functionality, so we test it doesn't raise an error
        pq_data = load_pq_data()
        try:
            # This should copy to clipboard without error
            export(pq_data, file_format='auto')
            # If we get here without exception, the test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Auto behavior for DataFrames failed: {e}")

    def test_display_format(self):
        # Test explicit display format
        pq_data = load_pq_data()
        trend = vi.create_trend(data=pq_data, metric="Collaboration_hours", hrvar="LevelDesignation")
        try:
            export(trend, file_format='display')
            # If we get here without exception, the test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Display format failed: {e}")

    def test_invalid_format_combinations(self):
        # Test that invalid combinations raise appropriate errors
        pq_data = load_pq_data()
        trend = vi.create_trend(data=pq_data, metric="Collaboration_hours", hrvar="LevelDesignation")
        
        # Try to export DataFrame as PNG (should fail)
        with self.assertRaises(ValueError):
            export(pq_data, file_format='png')
        
        # Try to export plot to clipboard (should fail)
        with self.assertRaises(ValueError):
            export(trend, file_format='clipboard')
        
        # Try to display DataFrame (should fail)
        with self.assertRaises(ValueError):
            export(pq_data, file_format='display')

if __name__ == '__main__':
    unittest.main()