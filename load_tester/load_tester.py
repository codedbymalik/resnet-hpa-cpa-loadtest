# load_tester.py
# This script performs load testing by sending images from a test folder to a prediction endpoint.
# It uses a custom load testing framework (BarAzmoon) and simulates requests per second.

import os
import random
import time
import argparse
import requests
from barazmoon import BarAzmoon

# Define the folder containing images to use for testing
IMAGES_FOLDER = os.path.join(os.getcwd(), "test_images")

# Create a list of valid image file paths from the folder
IMAGE_PATHS = [
    os.path.join(IMAGES_FOLDER, f)
    for f in os.listdir(IMAGES_FOLDER)
    if f.lower().endswith(('.jpg', '.jpeg', '.png'))
]

# Ensure that there are images available for testing
if not IMAGE_PATHS:
    raise SystemExit(f"No images found in {IMAGES_FOLDER}")

# Subclass BarAzmoon to define how to send requests and handle responses
class MyLoadTester(BarAzmoon):
    def get_request_data(self):
        # Randomly select an image and read its bytes to send as request data
        image_path = random.choice(IMAGE_PATHS)
        data_id = os.path.basename(image_path)
        with open(image_path, "rb") as f:
            image_data = f.read()
        return data_id, image_data

    def process_response(self, data_id, response_json):
        # Check if the response indicates success and log the result with a status icon
        success = response_json.get("success", False)
        status_icon = "✓" if success else "✗"
        print(f"[{status_icon}] {data_id} – {response_json}")
        return success


# Entry point for script execution – parse arguments and start load test
if __name__ == "__main__":
    # Define and parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True, help="URL of the prediction endpoint")
    parser.add_argument("--workload", nargs="+", type=int, default=[5, 5, 5], help="List of requests per second")
    args = parser.parse_args()

    # Instantiate the tester with parsed arguments and start the load test
    tester = MyLoadTester(
        workload=args.workload,
        endpoint=args.endpoint,
        http_method="post"
    )
    tester.start()
