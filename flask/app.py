import os
import requests
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from routes import api

# Configuration
WORKSPACE_ROOT = os.path.join(os.getcwd(), "petrophysics-workplace")
VITE_DEV_SERVER = os.environ.get('VITE_URL', 'http://localhost:5173')
IS_PRODUCTION = os.environ.get('NODE_ENV') == 'production'

def create_app():
    app = Flask(__name__, static_folder='../dist')
    CORS(app)
    
    # Register API routes BEFORE catch-all proxy
    app.register_blueprint(api, url_prefix='/api')
    
    # Development: Proxy to Vite dev server or serve static files in production
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def proxy_or_serve(path):
        if IS_PRODUCTION:
            # Serve static files in production
            if path and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            return send_from_directory(app.static_folder, 'index.html')
        else:
            # Proxy to Vite dev server in development
            try:
                url = f"{VITE_DEV_SERVER}/{path}"
                resp = requests.get(url, stream=True, headers=dict(request.headers))
                return resp.content, resp.status_code, dict(resp.headers)
            except Exception as e:
                return f"Vite dev server not available: {str(e)}", 502
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    print(f"Flask server starting on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
