# config.py


config = {
    # Fixed parameters (excluded from parameter sampling)
    "canvas_size": (1024, 1024),   # Size of the canvas (width, height) for
    # all images
    "num_images": 100,            # Number of images to generate
    "sampling_method": "LHS",    # Sampling method: "LHS" or "random"
    "DC_OFFSET": 0.5,            # Baseline offset to keep values positive

    # Parameter ranges for sampling
    "parameter_ranges": {
        "major_axis": (300, 400),
        "minor_axis": (300, 400),
        "angle_rotation": (0, 180),
        "erf_rolloff": (0.01, 0.1),    # Adjusted range for more noticeable
        # effect
        "gaussian_noise": (0.03, 0.05),
        "asymmetry_x": (-0.5, 0.5),
        "asymmetry_y": (-0.5, 0.5),

        # Perlin noise parameters
        "perlin_scale": (10, 100),
        "perlin_octaves": (1, 5),
        "perlin_persistence": (0.1, 0.9),
        "perlin_lacunarity": (1.5, 3.0),
        "perlin_amplitude": (0.1, 1.0)  # Amplitude of Perlin noise
    }
}
