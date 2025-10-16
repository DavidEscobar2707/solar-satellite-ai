import os
import sys

# Add your project directory to the Python path
# Replace 'yourusername' with your actual PythonAnywhere username
path = '/home/yourusername/solar_ai_backend'  # Update this path based on where you upload your files
if path not in sys.path:
    sys.path.append(path)

# Optional: Set environment variable if needed (PythonAnywhere handles this via dashboard)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_ai_backend.settings')

# Import your FastAPI app
from solar_ai_backend.main import app

# This is the application that will be called by the WSGI server
application = app
