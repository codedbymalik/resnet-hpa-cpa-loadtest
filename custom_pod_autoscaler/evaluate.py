#!/usr/bin/env python3
import os
import sys
import math
import json

# target latency threshold (seconds)
TARGET_LATENCY = float(os.getenv("TARGET_LATENCY", "0.5"))

def main():
    # read the metric value from STDIN
    raw = sys.stdin.read().strip()
    try:
        observed = float(raw)
    except:
        observed = 0.0

    # compute desired replicas = ceil(p95 / target)
    # ensures enough pods so each can meet the target latency
    if observed <= 0:
        desired = 1
    else:
        desired = math.ceil(observed / TARGET_LATENCY)

    # at least 1 replica
    desired = max(1, desired)
    # print(desired)
    
    evaluation = {}
    evaluation["targetReplicas"] = desired

        # Output JSON to stdout
    sys.stdout.write(json.dumps(evaluation))

if __name__ == "__main__":
    main()
