import sys
import os

# Add flask directory to path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'flask'))

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
