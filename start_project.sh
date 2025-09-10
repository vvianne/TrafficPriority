#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t ryu-mininet-env .

# Run the Docker container
echo "Running the container..."
docker run --privileged -it ryu-mininet-env