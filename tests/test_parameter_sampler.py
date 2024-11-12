# test_parameter_sampler.py

import unittest
import os
from src.parameter_sampler import get_sampled_parameters
from config import config

class TestParameterSampler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure the test_results directory exists
        cls.test_dir = "tests/test_results"
        os.makedirs(cls.test_dir, exist_ok=True)

    def test_sample_parameters_lhs(self):
        # Set up test-specific config for sampling
        num_samples = 5  # Use a small number for quick testing
        config["num_images"] = num_samples
        config["sampling_method"] = "LHS"
        
        # Run parameter sampling
        parameters = get_sampled_parameters()

        # Check the number of samples generated
        self.assertEqual(len(parameters), num_samples, 
                         f"Expected {num_samples} samples, but got {len(parameters)}")

        # Verify each parameter is within the specified range
        for param_set in parameters:
            for param_name, range_vals in config["parameter_ranges"].items():
                if isinstance(range_vals, dict):
                    # Handle nested ranges (e.g., perlin parameters)
                    for sub_param, (min_val, max_val) in range_vals.items():
                        param_value = param_set[f"{param_name}_{sub_param}"]
                        self.assertTrue(min_val <= param_value <= max_val,
                                        f"{param_name}_{sub_param} value {param_value} is out of range ({min_val}, {max_val})")
                else:
                    # Handle simple ranges
                    min_val, max_val = range_vals
                    param_value = param_set[param_name]
                    self.assertTrue(min_val <= param_value <= max_val,
                                    f"{param_name} value {param_value} is out of range ({min_val}, {max_val})")

    def test_sample_parameters_random(self):
        # Set up test-specific config for random sampling
        num_samples = 5
        config["num_images"] = num_samples
        config["sampling_method"] = "random"
        
        # Run parameter sampling
        parameters = get_sampled_parameters()

        # Check the number of samples generated
        self.assertEqual(len(parameters), num_samples,
                         f"Expected {num_samples} samples, but got {len(parameters)}")

        # Verify each parameter is within the specified range
        for param_set in parameters:
            for param_name, range_vals in config["parameter_ranges"].items():
                if isinstance(range_vals, dict):
                    # Handle nested ranges (e.g., perlin parameters)
                    for sub_param, (min_val, max_val) in range_vals.items():
                        param_value = param_set[f"{param_name}_{sub_param}"]
                        self.assertTrue(min_val <= param_value <= max_val,
                                        f"{param_name}_{sub_param} value {param_value} is out of range ({min_val}, {max_val})")
                else:
                    # Handle simple ranges
                    min_val, max_val = range_vals
                    param_value = param_set[param_name]
                    self.assertTrue(min_val <= param_value <= max_val,
                                    f"{param_name} value {param_value} is out of range ({min_val}, {max_val})")

    def test_save_sampled_parameters(self):
        # Save sampled parameters to a file for verification
        parameters = get_sampled_parameters()
        output_path = os.path.join(self.test_dir, "sampled_parameters.txt")

        # Write parameters to the output file
        with open(output_path, "w") as f:
            for i, param_set in enumerate(parameters, 1):
                f.write(f"Sample {i}: {param_set}\n")

        # Check if the output file was created
        self.assertTrue(os.path.isfile(output_path), "Sampled parameters file was not created")

if __name__ == "__main__":
    unittest.main()
