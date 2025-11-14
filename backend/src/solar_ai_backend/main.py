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

app = FastAPI(title="BackyardLeadAI Backend", version="0.1.0", description="Backend API for generating landscaping leads by detecting undeveloped backyards")

# Add CORS middleware for frontend integration
# Note: For production, you may want to use a regex pattern or environment variable for origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lovable.app",
        "https://www.lovable.app",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Vercel deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")

