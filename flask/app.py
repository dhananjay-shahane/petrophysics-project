import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from routes import api

# Configuration
WORKSPACE_ROOT = os.path.join(os.getcwd(), "petrophysics-workplace")
IS_PRODUCTION = os.environ.get('NODE_ENV') == 'production'

def create_app():
    # In production, serve static files from dist/public
    static_folder = '../dist/public' if IS_PRODUCTION else None
    app = Flask(__name__, static_folder=static_folder)
    CORS(app)
    
    # Register API routes
    app.register_blueprint(api, url_prefix='/api')
    
    @app.route('/health')
    def health():
        return {'status': 'ok'}
    
    # In production, serve frontend static files
    if IS_PRODUCTION:
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_frontend(path):
            if path and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            return send_from_directory(app.static_folder, 'index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('FLASK_PORT', 5001))
    host = '0.0.0.0' if IS_PRODUCTION else 'localhost'
    print(f"Flask server starting on http://{host}:{port}")
    print(f"Mode: {'PRODUCTION' if IS_PRODUCTION else 'DEVELOPMENT'}")
    app.run(host=host, port=port, debug=not IS_PRODUCTION)
