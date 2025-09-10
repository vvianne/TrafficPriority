#!/bin/bash

# Start Ryu in the background
ryu-manager /app/priority_ryu_controller.py &

# Run the Mininet topology script
python3 /app/ryu_topo.py
