#!/usr/bin/env bash

set -u

CLIENT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_DIR="$(cd -- "$CLIENT_DIR/../supa-fighta" && pwd)"
PYTHON_BIN="$CLIENT_DIR/.venv/bin/python"
SERVER_PID=""
CLIENT_PIDS=()

cleanup() {
    for pid in "${CLIENT_PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done

    if [[ -n "$SERVER_PID" ]]; then
        kill "$SERVER_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Missing WSL Python environment: $PYTHON_BIN"
    echo "Create it with: python3 -m venv .venv"
    exit 1
fi

if [[ ! -d "$SERVER_DIR/node_modules" ]]; then
    echo "Installing server dependencies..."
    (cd "$SERVER_DIR" && npm install) || exit 1
fi

echo "Starting local server..."
(cd "$SERVER_DIR" && node src/server.js) &
SERVER_PID=$!

sleep 1
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "The local server failed to start."
    wait "$SERVER_PID"
    exit 1
fi

run_client() {
    local data_file="$1"
    cd "$CLIENT_DIR" || exit 1

    # Override the normal hosted URL only for this debug process.
    "$PYTHON_BIN" -c '
import sys
sys.path.insert(0, "src")
import config
config.WS_URL = "ws://localhost:3000"
from main import main
main(sys.argv[1])
' "$data_file"
}

echo "Opening two local players..."
run_client "player-one.dat" &
CLIENT_PIDS+=("$!")
run_client "player-two.dat" &
CLIENT_PIDS+=("$!")

wait "${CLIENT_PIDS[0]}"
wait "${CLIENT_PIDS[1]}"
