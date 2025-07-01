# resnet-hpa-cpa-comparision
# ResNet HPA vs CPA Comparison 🚀

This project simulates and compares **Horizontal Pod Autoscaler (HPA)** and **Custom Pod Autoscaler (CPA)** for an image classification service using a ResNet18 model. It demonstrates how load can be dispatched, processed, and scaled in a Kubernetes environment using custom metrics (like latency) and Prometheus monitoring.

## 🧠 Core Components

### 1. **Dispatcher (FastAPI)**
Receives images via `/predict`, queues them, and forwards to replicas (inference servers) using round-robin logic.

### 2. **Replica (Inference Server)**
A Flask-based microservice that loads ResNet18 and classifies images.

### 3. **Load Tester (`barazmoon`)**
Generates HTTP requests with random images to simulate user load. It helps evaluate system behavior under different loads.

### 4. **Prometheus**
Monitors system performance like request rate, queue length, and latency.

### 5. **Custom Pod Autoscaler (CPA)**
Scales replicas based on latency metrics collected from Prometheus.

---

## 🧰 Prerequisites

- Python ≥ 3.8
- Docker + Docker Desktop (Mac)
- Minikube (for local Kubernetes)
- `kubectl` CLI
- Git

---

## 📦 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/resnet-hpa-cpa-comparision.git
cd resnet-hpa-cpa-comparision
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Prepare Image Data

Place your test `.jpg`/`.jpeg` images inside a folder:

```bash
mkdir images
# add your JPEGs to images/
```

---

## 🧪 Run Locally Without Kubernetes (Testing Mode)

### Run Replica (Model Server)

```bash
python inference_server.py
# Should run on http://localhost:6000
```

### Run Dispatcher

```bash
python dispatcher.py
# Should run on http://localhost:5052
```

### Run Load Tester

Edit `my_load_test.py` to point to the correct image folder and dispatcher URL, then run:

```bash
python my_load_test.py
```

---

## 🧠 Custom Autoscaler Setup with Minikube

### 1. Start Minikube

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

### 2. Deploy Prometheus

```bash
kubectl apply -f k8s/prometheus/
```

### 3. Deploy Inference Replicas

```bash
kubectl apply -f k8s/deployment.yaml
```

### 4. Apply CPA Script

This uses:

- `metric.py`: Pulls p95 latency from Prometheus
- `evaluate.py`: Outputs desired replicas based on latency threshold

### 5. View Metrics

Access Prometheus dashboard:

```bash
minikube service prometheus --url
```

---

## 📊 Metrics Tracked

| Metric | Description |
|--------|-------------|
| `dispatcher_queue_length` | Number of requests in queue |
| `dispatcher_enqueued_requests_total` | Count of enqueued items |
| `inference_in_progress` | Current in-flight requests |
| `inference_latency_seconds` | Request processing time |

---

## 📁 Project Structure

```bash
.
├── dispatcher/              # FastAPI-based dispatcher
├── inference_server.py      # Replica (ResNet18 inference)
├── load_tester/             # Custom load testing module
├── evaluate.py              # CPA decision logic
├── metric.py                # p95 latency collector
├── Dockerfile(s)
├── k8s/                     # Kubernetes manifests
├── requirements.txt
└── README.md
```

---

## 🤖 Custom Pod Autoscaler (CPA)

- Fetches p95 latency every 10s via `metric.py`
- Decides replica count using `evaluate.py`
- Updates Kubernetes replica count dynamically

---

## 🧪 Sample Result (CPA Load Test)

| Time | Replica Count | p95 Latency |
|------|----------------|-------------|
| -s   | 0              | 0s        |
| -s   | 0              | 0s        |

---

## 🧠 Future Ideas

- Integrate Grafana dashboards
- Compare CPU-based HPA with latency-based CPA visually
- Add support for autoscaling dispatcher

---

## 💬 Feedback or Issues?

Please [open an issue](https://github.com/coded-by-malik/resnet-hpa-cpa-comparision/issues) or submit a pull request.

---

## 🧾 License

MIT License © 2025