# inference_server.py

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
start_http_server(8002)  # Prometheus will scrape this port

# --- Flask setup ---
app = Flask(__name__)

# Load ResNet18 with default weights & preprocessing
weights = ResNet18_Weights.DEFAULT
model = models.resnet18(weights=weights)
model.eval()
transform = weights.transforms()
class_labels = weights.meta["categories"]

# Thread‐safe in‐flight counter
lock = threading.Lock()
in_progress = 0

@app.route('/predict', methods=['POST'])
def predict():
    global in_progress

    inprog.inc()
    start_ts = time.time()
    with lock:
        in_progress += 1

    try:
        img_file = request.files.get('image')
        if not img_file:
            return jsonify({"error": "No image file provided", "success": False}), 400

        # (Optional) save for debug
        img_file.save("debug_received.jpg")
        img = Image.open("debug_received.jpg").convert("RGB")

        # Preprocess & inference
        tensor = transform(img).unsqueeze(0)
        with torch.no_grad():
            out = model(tensor)
        probs = torch.nn.functional.softmax(out[0], dim=0)
        top_idx = int(probs.argmax())
        top_label = class_labels[top_idx]
        confidence = float(probs[top_idx])

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
        # record latency and decrement gauges/counters
        latency.observe(time.time() - start_ts)
        inprog.dec()
        with lock:
            in_progress -= 1

@app.route('/metric', methods=['GET'])
def metric():
    # Optional HTTP summary of in_progress
    with lock:
        return jsonify({
            "inProgress": in_progress
        })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000)
