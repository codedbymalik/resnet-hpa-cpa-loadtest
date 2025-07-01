#!/usr/bin/env python3
import requests
import math
import sys
import os

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL","http://localhost:9090")
# Use histogram_quantile for p95 over the last minute
QUERY = (
    'histogram_quantile(0.95, '
    'sum(rate(inference_latency_seconds_bucket[1m])) by (le))'
)

def fetch_p95():
    try:
        resp = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": QUERY},
            timeout=5
        )
        resp.raise_for_status()
        payload = resp.json()
        # Debug print if you need it:
        print("Prometheus response:", payload, file=sys.stderr)

        results = payload.get("data", {}).get("result", [])
        if not results:
            return 0.0

        # value = [ timestamp, value_str ]
        value_str = results[0].get("value", [None, "0"])[1]
        val = float(value_str)
        if math.isnan(val):
            return 0.0
        return val

    except Exception as e:
        # In case of any error, log to stderr and return 0
        print(f"Error fetching metric: {e}", file=sys.stderr)
        return 0.0

if __name__ == "__main__":
    p95_latency = fetch_p95()
    print(p95_latency)
    sys.stdout.write(str(p95_latency))
