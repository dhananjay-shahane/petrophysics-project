import os
from flask import Flask
from flask_cors import CORS

# Configuration
WORKSPACE_ROOT = os.path.join(os.getcwd(), "petrophysics-workplace")
VITE_DEV_SERVER = os.environ.get('VITE_URL', 'http://localhost:5173')
IS_PRODUCTION = os.environ.get('NODE_ENV') == 'production'

def create_app():
    app = Flask(__name__, static_folder='../dist/public')
    CORS(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    print(f"Flask server starting on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
