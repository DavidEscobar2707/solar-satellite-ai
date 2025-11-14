"""
Vercel serverless function wrapper for FastAPI backend.
This file is used by Vercel to deploy the FastAPI backend as serverless functions.
"""
import sys
import os
from pathlib import Path

# Add backend/src to Python path
backend_path = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

# Import Mangum handler
from mangum import Mangum

# Import FastAPI app
from solar_ai_backend.main import app

# Create Mangum handler for Vercel
handler = Mangum(app, lifespan="off")

# Export handler for Vercel
__all__ = ["handler"]

