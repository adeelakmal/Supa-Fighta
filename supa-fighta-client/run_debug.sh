#!/bin/bash

# Load environment variables from .env file
set -a
source ../supa-fighta/.env
set +a

# Point debug clients at the local server using the same configured port.
export SUPA_FIGHTA_WS_URL="ws://localhost:${PORT:-8080}"

# Run the Node.js server
echo "Starting Node.js server..."
node ../supa-fighta/src/server.js & NODE_PID=$!
echo "Waiting for Node.js server to start..."
sleep 1

# Run the Python client
echo "Starting Python client..."
.././venv/Scripts/python.exe src/main.py --datafile player_credentials.json & PY_PID1=$!
.././venv/Scripts/python.exe src/main.py --datafile player_credentials2.json & PY_PID2=$!

# Wait for the Python client to finish
wait $PY_PID1
wait $PY_PID2

# Stop Node.js server when the Python client exits
echo "Stopping Node.js server..."
kill $NODE_PID
echo "All processes finished."
