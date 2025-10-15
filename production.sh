#!/bin/bash

# Production startup script
# Flask serves both API and static files on port 5000

export NODE_ENV=production
export FLASK_PORT=3000

echo "Starting production server..."
uv run python flask/app.py
