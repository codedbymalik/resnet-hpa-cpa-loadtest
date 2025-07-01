import os
import random
import time
import argparse
import requests
from barazmoon import BarAzmoon

# Set up image paths
IMAGES_FOLDER = os.path.join(os.getcwd(), "test_images")
IMAGE_PATHS = [
    os.path.join(IMAGES_FOLDER, f)
    for f in os.listdir(IMAGES_FOLDER)
    if f.lower().endswith(('.jpg', '.jpeg', '.png'))
]

if not IMAGE_PATHS:
    raise SystemExit(f"No images found in {IMAGES_FOLDER}")

# class MyLoadTester(BarAzmoon):
#     def get_request_data(self):
#         """Randomly selects an image path to send as request data."""
#         return random.choice(IMAGE_PATHS)

#     def send_request(self, image_path):
#         """Sends a POST request with the selected image and measures latency."""
#         start_time = time.time()
#         with open(image_path, "rb") as f:
#             files = {
#                 "image": (os.path.basename(image_path), f, "image/jpeg")
#             }
#             try:
#                 response = requests.post(self.endpoint, files=files)
#             except Exception as e:
#                 print(f"[✗] Request failed: {e}")
#                 response = None
#         return response, start_time

#     def process_response(self, sent_id, result):
#         """Processes the response and prints result info."""
#         response, start_time = result
#         latency = time.time() - start_time

#         if not isinstance(response, requests.Response):
#             print(f"[✗] {sent_id} – Invalid or no response")
#             return False

#         try:
#             json_data = response.json()
#         except Exception as e:
#             print(f"[✗] {sent_id} – Failed to parse JSON: {e}")
#             return False

#         success = json_data.get("success", False)
#         status_icon = "✓" if success else "✗"
#         print(f"[{status_icon}] {sent_id} – {response.status_code} – {latency:.3f}s – {json_data}")
        # return success
        
class MyLoadTester(BarAzmoon):
    def get_request_data(self):
        """Returns a (filename, image bytes) tuple."""
        image_path = random.choice(IMAGE_PATHS)
        data_id = os.path.basename(image_path)
        with open(image_path, "rb") as f:
            image_data = f.read()
        return data_id, image_data

    def process_response(self, data_id, response_json):
        """Processes the JSON response."""
        success = response_json.get("success", False)
        status_icon = "✓" if success else "✗"
        print(f"[{status_icon}] {data_id} – {response_json}")
        return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True, help="URL of the prediction endpoint")
    parser.add_argument("--workload", nargs="+", type=int, default=[5, 5, 5], help="List of requests per second")
    args = parser.parse_args()

    tester = MyLoadTester(
        workload=args.workload,
        endpoint=args.endpoint,
        http_method="post"
    )
    tester.start()
