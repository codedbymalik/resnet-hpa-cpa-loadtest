# dispatcher.py
# This script sets up a dispatcher that receives inference requests via a Flask API,
# queues them in Redis, and asynchronously forwards them to a model inference server.
# It also exposes Prometheus metrics to monitor queue length and throughput.

from flask import Flask, request, jsonify 
import redis, os, requests # Redis for queueing requests, os for env vars, requests to forward requests
from prometheus_client import Gauge, Counter, start_http_server # For metrics monitoring

# Initialize the Flask application and connect to Redis
app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST","localhost"), port=6379, db=0) # Connect to Redis queue

# Define Prometheus metrics for queue length and number of enqueued/dequeued requests
queue_len = Gauge("dispatcher_queue_length", "Requests pending")
enq = Counter("dispatcher_enqueued_total", "Total enqueued")
deq = Counter("dispatcher_dequeued_total", "Total dequeued")

# Inference server endpoint to forward requests to
INFERENCE_URL = os.getenv("INFERENCE_URL","http://localhost:6000/predict") # URL to forward inference requests

# Flask route to accept POST requests with an image file and queue the data in Redis
@app.route("/dispatch", methods=["POST"])
def dispatch():
    img = request.files.get("image")
    if not img:
        return jsonify(success=False, error="no image"), 400

    # Read the image file data and push it to the Redis queue
    data = img.read()
    r.rpush("queue", data)
    enq.inc()
    queue_len.set(r.llen("queue"))
    # Return a success response after queueing the image
    return jsonify(success=True)

# Worker loop that runs in a separate thread to process queued images and send them for inference
def worker_loop():
    while True:
        # Block and wait for an item in the Redis queue with a timeout
        item = r.blpop("queue", timeout=5)
        if not item:
            continue
        _, data = item
        # Send the dequeued image to the inference server via HTTP POST
        try:
            resp = requests.post(INFERENCE_URL,
                                 files={"image": ("img.jpg", data, "image/jpeg")})
        except Exception as e:
            print(e)
        deq.inc()
        queue_len.set(r.llen("queue"))

if __name__=="__main__":
    # Start Prometheus metrics server on port 8001
    start_http_server(8001)
    from threading import Thread
    # Start the worker loop in a background thread
    Thread(target=worker_loop, daemon=True).start()
    # Start the Flask web server to listen for dispatch requests
    app.run(host="0.0.0.0", port=7000)
