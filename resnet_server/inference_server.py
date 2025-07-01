# inference_server.py
# inference_server.py
# This script sets up a Flask-based server that loads a ResNet18 model to handle image classification requests.
# It uses Prometheus to collect metrics such as inference latency and number of concurrent requests.

import time
import threading

from flask import Flask, request, jsonify
from prometheus_client import Gauge, Histogram, start_http_server
import torch
from torchvision import models
from torchvision.models import ResNet18_Weights
from PIL import Image

# --- Prometheus instrumentation ---
inprog = Gauge("inference_inprogress", "Requests in flight")
latency = Histogram("inference_latency_seconds", "Inference latency in seconds")
# Start Prometheus metrics server on port 8002
start_http_server(8002)  # Prometheus will scrape this port

# --- Flask setup ---
# Initialize Flask app
app = Flask(__name__)

# Load pre-trained ResNet18 model with default weights and preprocessing pipeline
weights = ResNet18_Weights.DEFAULT
model = models.resnet18(weights=weights)
model.eval()
transform = weights.transforms()
class_labels = weights.meta["categories"]

# Create a thread-safe lock and counter for tracking in-progress requests
lock = threading.Lock()
in_progress = 0

# Prediction endpoint that accepts image uploads and returns classification results
@app.route('/predict', methods=['POST'])
def predict():
    global in_progress

    inprog.inc()
    start_ts = time.time()
    with lock:
        in_progress += 1

    try:
        # Retrieve uploaded image from the request
        img_file = request.files.get('image')
        if not img_file:
            return jsonify({"error": "No image file provided", "success": False}), 400

        # (Optional) save for debug
        img_file.save("debug_received.jpg")
        # Load the saved image and ensure it's in RGB format
        img = Image.open("debug_received.jpg").convert("RGB")

        # Preprocess image and add batch dimension
        tensor = transform(img).unsqueeze(0)
        with torch.no_grad():
            out = model(tensor)
        # Compute softmax probabilities for classification output
        probs = torch.nn.functional.softmax(out[0], dim=0)
        top_idx = int(probs.argmax())
        top_label = class_labels[top_idx]
        confidence = float(probs[top_idx])

        # Build and return the JSON response with top prediction and confidence
        return jsonify({
            "success": True,
            "prediction": {
                "class_index": top_idx,
                "label": top_label,
                "confidence": round(confidence, 4)
            }
        })

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

    finally:
        # Record latency and update metrics after the request is processed
        latency.observe(time.time() - start_ts)
        inprog.dec()
        with lock:
            in_progress -= 1

# Endpoint to expose in-progress request count as a simple JSON for debug
@app.route('/metric', methods=['GET'])
def metric():
    # Optional HTTP summary of in_progress
    with lock:
        return jsonify({
            "inProgress": in_progress
        })

# Run the Flask app on all interfaces at port 6000
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000)
