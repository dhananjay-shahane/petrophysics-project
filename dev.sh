#!/bin/bash

# Start Flask API server in background on port 5001
export FLASK_PORT=5001
uv run python flask/app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 2

# Start Vite dev server on port 5000 (frontend)
node_modules/.bin/vite --port 3000 --host 0.0.0.0

# Cleanup on exit
kill $FLASK_PID 2>/dev/null
