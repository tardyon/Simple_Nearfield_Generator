# test_output_manager.py

import unittest
import os
import numpy as np
from datetime import datetime
from tifffile import imread
from src.output_manager import create_output_folder, save_image, log_parameters

class TestOutputManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure the test_output directory exists
        cls.test_dir = "test_output"
        os.makedirs(cls.test_dir, exist_ok=True)

    def test_create_output_folder(self):
        # Use test_dir for output and check folder creation
        folder_path = create_output_folder(self.test_dir)
        self.assertTrue(os.path.exists(folder_path))
        
        # Create the folder again to check timestamped creation
        folder_path_with_timestamp = create_output_folder(self.test_dir)
        self.assertTrue(os.path.exists(folder_path_with_timestamp))
        self.assertNotEqual(folder_path, folder_path_with_timestamp)

        # Verify the timestamp format in the folder name
        timestamp_pattern = r"\d{8}_\d{6}$"  # Matches YYYYMMDD_HHMMSS at end of string
        self.assertRegex(folder_path_with_timestamp, timestamp_pattern,
                         "Timestamp not appended correctly to the folder name")

    def test_save_image(self):
        output_folder = create_output_folder(self.test_dir)
        filename = "test_image.tiff"
        # Create a dummy 16-bit image
        image = (np.random.rand(512, 512) * 65535).astype(np.uint16)
        
        # Save the image
        save_image(image, filename, output_folder)
        saved_path = os.path.join(output_folder, filename)
        self.assertTrue(os.path.isfile(saved_path))
        
        # Verify the saved image is 16-bit
        saved_image = imread(saved_path)
        self.assertEqual(saved_image.dtype, np.uint16)

    def test_log_parameters(self):
        csv_path = os.path.join(self.test_dir, "parameters.csv")
        filename = "test_image.tiff"
        parameters = {
            "major_axis": 50,
            "minor_axis": 30,
            "angle_rotation": 45,
            "erf_rolloff": 1.5,
            "gaussian_noise": 0.02,
            "perlin_scale": 0.5,
            "perlin_octaves": 3,
            "perlin_persistence": 0.7,
            "perlin_lacunarity": 2.0,
            "asymmetry_x": 0.3,
            "asymmetry_y": 0.1
        }

        # Log the parameters
        log_parameters(csv_path, filename, parameters)
        
        # Check if the CSV was created and has the correct headers and values
        with open(csv_path, 'r') as csv_file:
            lines = csv_file.readlines()
            self.assertEqual(len(lines), 2)  # Header + 1 data row

            # Verify headers
            headers = lines[0].strip().split(',')
            expected_headers = ['filename'] + list(parameters.keys())
            self.assertEqual(headers, expected_headers)

            # Verify values
            values = lines[1].strip().split(',')
            expected_values = [filename] + [str(v) for v in parameters.values()]
            self.assertEqual(values, expected_values)

if __name__ == "__main__":
    unittest.main()
