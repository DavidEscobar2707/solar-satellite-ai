import logging
import os
from fastapi import FastAPI

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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")

