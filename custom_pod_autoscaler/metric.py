# metric.py
# This script queries Prometheus for the 95th percentile latency of inference requests
# using a histogram_quantile function over the past 1 minute. It is designed to provide
# latency metrics to the custom pod autoscaler.
#!/usr/bin/env python3
import requests
import math
import sys
import os

# Get Prometheus server URL from environment variable or use default
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL","http://localhost:9090")
# Prometheus query to compute the 95th percentile latency from histogram buckets
QUERY = (
    'histogram_quantile(0.95, '
    'sum(rate(inference_latency_seconds_bucket[1m])) by (le))'
)

# Function to fetch the 95th percentile inference latency from Prometheus
def fetch_p95():
    try:
        # Send HTTP GET request to Prometheus with the defined query
        resp = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": QUERY},
            timeout=5
        )
        resp.raise_for_status()
        # Parse the JSON response from Prometheus
        payload = resp.json()
        # Debug print if you need it:
        print("Prometheus response:", payload, file=sys.stderr)

        # Extract the results list from the response payload
        results = payload.get("data", {}).get("result", [])
        if not results:
            return 0.0

        # Get the string value from the first result's 'value' field
        value_str = results[0].get("value", [None, "0"])[1]
        val = float(value_str)
        # Handle NaN values gracefully
        if math.isnan(val):
            return 0.0
        return val

    # Handle and report any exceptions during the fetch process
    except Exception as e:
        # In case of any error, log to stderr and return 0
        print(f"Error fetching metric: {e}", file=sys.stderr)
        return 0.0

# Execute fetch_p95 and write the result to stdout if this script is run directly
if __name__ == "__main__":
    p95_latency = fetch_p95()
    print(p95_latency)
    sys.stdout.write(str(p95_latency))
