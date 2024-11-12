# parameter_sampler.py

import numpy as np
from scipy.stats import qmc  # For Latin Hypercube Sampling
from config import config

def sample_parameters(parameter_ranges, num_samples, method="LHS"):
    """
    Samples parameters within the specified ranges for generating Nearfield images.

    Parameters:
    - parameter_ranges (dict): Dictionary with parameter names as keys and (min, max) tuples or nested dicts.
    - num_samples (int): Number of samples to generate.
    - method (str): Sampling method; default is "LHS" (Latin Hypercube Sampling).

    Returns:
    - list of dicts: Each dict contains a unique set of parameters for an image.
    """
    parameters = []

    # Flatten parameter_ranges for LHS if method is "LHS"
    flattened_ranges = {}
    for param_name, range_vals in parameter_ranges.items():
        if isinstance(range_vals, dict):
            for sub_param, sub_range in range_vals.items():
                flattened_ranges[f"{param_name}_{sub_param}"] = sub_range
        else:
            flattened_ranges[param_name] = range_vals

    # Define parameters that should be integers
    integer_params = ["perlin_octaves"]

    if method == "LHS":
        # Perform Latin Hypercube Sampling for efficient coverage
        sampler = qmc.LatinHypercube(d=len(flattened_ranges))
        lhs_samples = sampler.random(n=num_samples)

        # Map LHS results to parameter ranges
        for i in range(num_samples):
            sample = {}
            for j, (param_name, (min_val, max_val)) in enumerate(flattened_ranges.items()):
                # Scale LHS value to the specified range
                value = min_val + lhs_samples[i, j] * (max_val - min_val)
                # Convert to integer if needed
                if param_name in integer_params:
                    value = int(round(value))
                sample[param_name] = value
            parameters.append(sample)

    elif method == "random":
        # Use simple random sampling within the range
        for _ in range(num_samples):
            sample = {}
            for param_name, range_vals in parameter_ranges.items():
                if isinstance(range_vals, dict):
                    for sub_param, (min_val, max_val) in range_vals.items():
                        value = np.random.uniform(min_val, max_val)
                        if f"{param_name}_{sub_param}" in integer_params:
                            value = int(round(value))
                        sample[f"{param_name}_{sub_param}"] = value
                else:
                    min_val, max_val = range_vals
                    value = np.random.uniform(min_val, max_val)
                    if param_name in integer_params:
                        value = int(round(value))
                    sample[param_name] = value
            parameters.append(sample)
    
    else:
        raise ValueError(f"Unknown sampling method: {method}")
    
    return parameters

def get_sampled_parameters():
    """
    Generates parameters for the number of images specified in config using LHS.
    """
    num_samples = config["num_images"]
    parameter_ranges = config["parameter_ranges"]
    sampling_method = config["sampling_method"]

    return sample_parameters(parameter_ranges, num_samples, method=sampling_method)
