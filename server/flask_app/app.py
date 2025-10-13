from flask import Flask
from flask_cors import CORS
from .routes.projects import projects_bp
from .routes.wells import wells_bp
from .routes.visualization import visualization_bp
import os

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Register blueprints
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(wells_bp, url_prefix='/api/wells')
    app.register_blueprint(visualization_bp, url_prefix='/api/visualization')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {"status": "ok", "message": "Flask server is running"}
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('FLASK_PORT', 5001))
    app.run(host='localhost', port=port, debug=True)
