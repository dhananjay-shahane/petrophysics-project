#!/bin/bash

# Start Vite dev server in background on port 5173
VITE_PORT=5173 npm run dev:vite &
VITE_PID=$!

# Wait a bit for Vite to start
sleep 2

# Start Flask server on port 5000
export VITE_URL=http://localhost:5173
export PORT=5000
uv run python flask/app.py

# Cleanup on exit
kill $VITE_PID 2>/dev/null
