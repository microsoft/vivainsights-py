import os
import unittest
import shutil

def run_tests():
    # Run the tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests')
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    
    # Return the result of the tests
    return result.wasSuccessful()

def cleanup_test_files(filenames):
    # Delete the specified test files in the root directory
    root_dir = '.'
    for filename in filenames:
        file_path = os.path.join(root_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

if __name__ == "__main__":
    tests_passed = run_tests()
    if tests_passed:
        files_to_delete = [
            'test_files.csv',
            'test_files.jpeg',
            'test_files.pdf',
            'test_files.png',            
            'test_files.svg'
        ]
        cleanup_test_files(filenames=files_to_delete)
    else:
        print("Tests failed. Not deleting test files.")