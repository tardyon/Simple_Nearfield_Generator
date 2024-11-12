# output_manager.py

import os
import csv
from tifffile import imwrite
from config import config  # Import configuration for potential usage in file paths

def create_output_folder(base_folder):
    """
    Creates a timestamped output folder to avoid overwriting.

    Parameters:
    - base_folder (str): Base path for the output folder.

    Returns:
    - str: Path to the created output folder.
    """
    output_folder = f"{base_folder}_{get_timestamp()}"
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

def save_image(image, filename, output_folder):
    """
    Saves an image to a TIFF file.

    Parameters:
    - image (numpy array): Image data to be saved.
    - filename (str): Name of the output file.
    - output_folder (str): Path to the folder where the image will be saved.
    """
    filepath = os.path.join(output_folder, filename)
    imwrite(filepath, image, dtype='uint16')

def log_parameters(csv_path, filename, params):
    """
    Logs the image parameters to a CSV file.

    Parameters:
    - csv_path (str): Path to the CSV file.
    - filename (str): Filename of the image.
    - params (dict): Dictionary of parameters used for generating the image.
    """
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["filename"] + list(params.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow({"filename": filename, **params})

def get_timestamp():
    """
    Returns a timestamp string for unique folder naming.

    Returns:
    - str: Timestamp in 'YYYYMMDD_HHMMSS' format.
    """
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")
