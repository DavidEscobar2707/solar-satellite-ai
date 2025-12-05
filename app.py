#!/usr/bin/env python3
"""
Entry point for Render deployment.
Sets up the correct Python path and imports the FastAPI app.
"""

import sys
import os

# Add the backend/src directory to Python path
backend_src_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
if backend_src_path not in sys.path:
    sys.path.insert(0, backend_src_path)

# Import and expose the FastAPI app
from solar_ai_backend.main import app

# For Render deployment
application = app
