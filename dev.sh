#!/bin/bash

# Start Vite dev server in background on port 5173
./node_modules/.bin/vite --port 5173 --host 0.0.0.0 &
VITE_PID=$!

# Wait for Vite to start
sleep 3

# Start Flask server on port 5000
export VITE_URL=http://localhost:5173
export PORT=5000
uv run python flask/app.py

# Cleanup on exit
kill $VITE_PID 2>/dev/null
