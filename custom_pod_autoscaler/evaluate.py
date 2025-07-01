# evaluate.py
# This script is used by the custom pod autoscaler to determine the desired number of replicas
# based on the observed latency metric. It reads a latency value from STDIN, compares it with a target,
# and outputs a JSON object with the recommended replica count.
#!/usr/bin/env python3
# Import necessary modules
import os
import sys
import math
import json

# Define the target latency threshold (in seconds), defaulting to 0.5s if not set in environment
TARGET_LATENCY = float(os.getenv("TARGET_LATENCY", "0.5"))

# Main function to compute and output the desired number of replicas
def main():
    # Read the observed latency value from standard input
    raw = sys.stdin.read().strip()
    # Attempt to convert the input to a float
    try:
        observed = float(raw)
    except:
        observed = 0.0

    # Calculate the number of replicas needed to meet the target latency.
    # If observed is less than or equal to zero, default to 1 replica.
    # Otherwise, divide observed latency by target and round up.
    if observed <= 0:
        desired = 1
    else:
        desired = math.ceil(observed / TARGET_LATENCY)

    # Ensure that at least 1 replica is always used
    desired = max(1, desired)
    # print(desired)
    
    # Build a JSON object containing the target number of replicas
    evaluation = {}
    evaluation["targetReplicas"] = desired

    # Output the evaluation result to stdout
    sys.stdout.write(json.dumps(evaluation))

# Run the main function when this script is executed
if __name__ == "__main__":
    main()
