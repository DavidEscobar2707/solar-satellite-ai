import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router
from .utils.env_loader import load_env_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Load environment variables from .env file
load_env_file()

app = FastAPI(title="Solar AI Backend", version="0.1.0")

# Add CORS middleware for Lovable integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lovable.app", "https://www.lovable.app"],  # Lovable's domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")

