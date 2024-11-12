# image_generator.py

import numpy as np
from scipy.special import erf
from noise import pnoise2
from scipy.ndimage import distance_transform_edt
from config import config

# Define a DC offset to ensure positive values
DC_OFFSET = 0.5  # This can be adjusted as needed to keep all values positive


def create_elliptical_mask(canvas_size,
                           major_axis, minor_axis, angle_rotation):
    """
    Creates a binary elliptical mask based on specified size and rotation.

    Parameters:
    - canvas_size (tuple): Size of the image canvas (width, height).
    - major_axis (float): Length of the major axis.
    - minor_axis (float): Length of the minor axis.
    - angle_rotation (float): Rotation angle of the ellipse in degrees.

    Returns:
    - numpy array: Binary mask where the elliptical region is 1 and the
    rest is 0.
    """
    width, height = canvas_size
    x, y = np.meshgrid(np.arange(width), np.arange(height))
    x_center, y_center = width / 2, height / 2

    # Rotate the coordinates by the specified angle
    theta = np.radians(angle_rotation)
    x_rot = (x - x_center) * np.cos(theta) + (y - y_center) * np.sin(theta)
    y_rot = -(x - x_center) * np.sin(theta) + (y - y_center) * np.cos(theta)

    # Define the ellipse mask
    ellipse_mask = ((x_rot / major_axis) ** 2 + (y_rot / minor_axis) ** 2) <= 1
    return ellipse_mask.astype(float)


def generate_perlin_noise(canvas_size, scale,
                          octaves, persistence, lacunarity, amplitude):
    """
    Generates a Perlin noise canvas with a specified amplitude and DC offset.

    Parameters:
    - canvas_size (tuple): Size of the canvas (width, height).
    - scale (float): Scale factor for Perlin noise.
    - octaves (int): Number of Perlin noise octaves.
    - persistence (float): Persistence factor controlling amplitude.
    - lacunarity (float): Lacunarity controlling frequency spacing.
    - amplitude (float): Amplitude of Perlin noise.

    Returns:
    - numpy array: Canvas with Perlin noise applied, offset to be positive.
    """
    width, height = canvas_size
    noise = np.zeros((width, height))

    # Generate Perlin noise in a vectorized manner
    for i in range(width):
        for j in range(height):
            noise_val = pnoise2(i / scale, j / scale, octaves=octaves,
                                persistence=persistence, lacunarity=lacunarity)
            noise[i, j] = noise_val * amplitude

    # Add DC offset from config
    return noise + config["DC_OFFSET"]


def apply_erf_rolloff(mask, rolloff):
    """
    Applies an ERF roll-off at the edges of the mask.

    Parameters:
    - mask (numpy array): The binary mask (1 inside the shape, 0 outside).
    - rolloff (float): Controls edge roll-off sharpness.

    Returns:
    - numpy array: Mask with an ERF roll-off applied at the edges.
    """
    # Compute signed distance transform (positive inside, negative outside)
    distance = distance_transform_edt(mask) - distance_transform_edt(1 - mask)

    # Apply erf roll-off based on distance
    return 0.5 * (1 + erf(distance * rolloff))


def apply_asymmetry(image, asymmetry_x, asymmetry_y):
    """
    Applies asymmetry to an image.

    Parameters:
    - image (numpy array): The base image.
    - asymmetry_x (float): Gradient effect in the x direction.
    - asymmetry_y (float): Gradient effect in the y direction.

    Returns:
    - numpy array: Image with asymmetry applied.
    """
    width, height = image.shape
    x_gradient = np.linspace(-asymmetry_x, asymmetry_x, width).reshape(-1, 1)
    y_gradient = np.linspace(-asymmetry_y, asymmetry_y, height).reshape(1, -1)

    # Apply gradients
    image += x_gradient + y_gradient
    return image


def apply_gaussian_noise(image, gaussian_noise):
    """
    Applies Gaussian noise to an image.

    Parameters:
    - image (numpy array): The base image.
    - gaussian_noise (float): Standard deviation of Gaussian noise to add.

    Returns:
    - numpy array: Image with Gaussian noise applied.
    """
    image += np.random.normal(0, gaussian_noise, image.shape)
    return np.clip(image, 0, 1)  # Clip values to stay within [0, 1]


def generate_nearfield_image(params):
    """
    Generates a Nearfield image based on specified parameters.
    """
    canvas_size = config["canvas_size"]
    return generate_nearfield_image_impl(params, canvas_size)


def generate_nearfield_image_impl(params, canvas_size):
    """
    Generates a Nearfield image based on specified parameters.

    Parameters:
    - params (dict): Dictionary of parameters for the Nearfield image.
    - canvas_size (tuple): Size of the output image (width, height).

    Returns:
    - numpy array: Generated Nearfield image.
    """
    # Step 1: Generate Perlin noise with DC offset
    perlin_noise = generate_perlin_noise(canvas_size, params["perlin_scale"],
                                         params["perlin_octaves"],
                                         params["perlin_persistence"],
                                         params["perlin_lacunarity"],
                                         params["perlin_amplitude"])

    # Step 2: Apply asymmetry
    perlin_noise = apply_asymmetry(perlin_noise,
                                   params["asymmetry_x"],
                                   params["asymmetry_y"])

    # Step 3: Create elliptical mask
    ellipse_mask = create_elliptical_mask(canvas_size, params["major_axis"],
                                          params["minor_axis"],
                                          params["angle_rotation"])

    # Step 4: Apply ERF roll-off to the ellipse mask
    ellipse_with_rolloff = apply_erf_rolloff(
        ellipse_mask, params["erf_rolloff"])

    # Step 5: Apply the mask with roll-off to the image
    masked_image = perlin_noise * ellipse_with_rolloff

    # Step 6: Apply Gaussian noise
    final_image = apply_gaussian_noise(masked_image, params["gaussian_noise"])

    # Scale the final image to 16-bit range and return
    return (final_image * 65535).astype(np.uint16)
