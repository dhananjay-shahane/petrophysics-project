# Start Vite dev server in background on port 5173
Start-Process -FilePath "node_modules/.bin/vite.cmd" -ArgumentList "--port 5173 --host 0.0.0.0"

# Wait for Vite to start
Start-Sleep -Seconds 3

# Set environment variables
$env:VITE_URL = "http://localhost:5173"
$env:PORT = "5000"

# Activate virtual environment (if exists)
# Example: replace with your actual venv path
# & ".\.venv\Scripts\Activate.ps1"

# Run Flask server
python flask/app.py

# Optional: Stop Vite server when Flask exits
Get-Process | Where-Object { $_.Path -like "*vite*" } | Stop-Process -Force
