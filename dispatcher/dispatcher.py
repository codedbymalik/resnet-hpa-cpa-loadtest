# dispatcher.py     - Entry point for handling image inference requests and routing to the backend model
from flask import Flask, request, jsonify 
import redis, os, requests # Redis for queueing requests, os for env vars, requests to forward requests
from prometheus_client import Gauge, Counter, start_http_server # For metrics monitoring

app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST","localhost"), port=6379, db=0) # Connect to Redis queue

# Prometheus metrics definitions
queue_len = Gauge("dispatcher_queue_length", "Requests pending")
enq = Counter("dispatcher_enqueued_total", "Total enqueued")
deq = Counter("dispatcher_dequeued_total", "Total dequeued")

INFERENCE_URL = os.getenv("INFERENCE_URL","http://localhost:6000/predict") # URL to forward inference requests

@app.route("/dispatch", methods=["POST"])
def dispatch():
    img = request.files.get("image")
    if not img:
        return jsonify(success=False, error="no image"), 400

    data = img.read()
    r.rpush("queue", data)
    enq.inc()
    queue_len.set(r.llen("queue"))
    return jsonify(success=True)

def worker_loop():
    while True:
        item = r.blpop("queue", timeout=5)
        if not item:
            continue
        _, data = item
        # call inference
        try:
            resp = requests.post(INFERENCE_URL,
                                 files={"image": ("img.jpg", data, "image/jpeg")})
        except Exception as e:
            print(e)
        deq.inc()
        queue_len.set(r.llen("queue"))

if __name__=="__main__":
    start_http_server(8001)
    from threading import Thread
    Thread(target=worker_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=7000)
