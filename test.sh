#!/bin/bash

# Load environment variables from .env file
set -a
source supa-fighta/.env
set +a

# Run the Node.js server
echo "Starting Node.js server..."
node supa-fighta/src/server.js & NODE_PID=$!
echo "Waiting for Node.js server to start..."
sleep 1

# Run the Python client
echo "Starting Python client..."
./venv/Scripts/python.exe supa-fighta-client/src/main.py & PY_PID=$!

# Wait for the Python client to finish
wait $PY_PID

# Stop Node.js server when the Python client exits
echo "Stopping Node.js server..."
kill $NODE_PID
echo "All processes finished."