import unittest
import os
import vivainsights as vi
from vivainsights.pq_data import load_pq_data
from PIL import Image, ImageDraw
from vivainsights import export



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

if __name__ == '__main__':
    unittest.main()