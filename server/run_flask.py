#!/usr/bin/env python3
import os
import sys

# Add the server directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from flask_app.app import create_app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('FLASK_PORT', 5001))
    print(f"Flask server starting on http://localhost:{port}")
    app.run(host='localhost', port=port, debug=False, use_reloader=False)
