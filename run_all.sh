#!/bin/bash

# Start Ryu in the background and bind to TCP port 6653 for Mininet RemoteController
echo "Starting Ryu controller on 0.0.0.0:6653..."
ryu-manager --ofp-tcp-listen 6653 /app/priority_ryu_controller.py &
RYU_PID=$!
echo "Ryu PID=$RYU_PID"

# Run the Mininet topology script
python3 /app/ryu_topo.py
