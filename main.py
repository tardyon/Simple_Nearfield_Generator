# main.py

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from config import config
from src.parameter_sampler import get_sampled_parameters
from src.output_manager import create_output_folder, save_image, log_parameters
from src.image_generator import generate_nearfield_image
from tqdm import tqdm


def generate_and_save_image(params, index, output_folder_path, csv_path):
    """
    Generates a Nearfield image and saves it along with its parameters.

    Parameters:
    - params (dict): Parameter set for the image generation.
    - index (int): Index of the image (for naming).
    - output_folder_path (str): Path to the folder where images will be saved.
    - csv_path (str): Path to the CSV file where parameters will be logged.

    Returns:
    - str: Filename of the generated image.
    """
    # Generate the Nearfield image
    image = generate_nearfield_image(params)

    # Define the image filename
    filename = f"nearfield_image_{index + 1:03}.tiff"

    # Save the image and log parameters
    save_image(image, filename, output_folder_path)
    log_parameters(csv_path, filename, params)

    return filename


def main():
    num_images = config["num_images"]
    output_folder = "output/images"

    # Step 2: Create the output folder
    output_folder_path = create_output_folder(output_folder)
    csv_path = os.path.join(output_folder_path, "parameters_log.csv")

    # Step 3: Generate parameter sets for each image
    parameter_sets = get_sampled_parameters()

    # Step 4: Use ProcessPoolExecutor to parallelize image generation with a
    # progress bar
    with ProcessPoolExecutor() as executor, \
         tqdm(total=num_images, desc="Generating Images",
              unit="image") as pbar:
        futures = {
            executor.submit(generate_and_save_image,
                            params, i, output_folder_path, csv_path): i
            for i, params in enumerate(parameter_sets)
        }

        # Collect results and update progress bar as tasks complete
        for future in as_completed(futures):
            try:
                filename = future.result()
                pbar.set_postfix_str(f"Last saved: {filename}")
            except Exception as e:
                print(f"Error generating image: {e}")
            finally:
                pbar.update(1)  # Increment progress bar by 1 for each =
                # completed task


if __name__ == "__main__":
    main()
