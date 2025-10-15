import os
from functools import lru_cache
from typing import Optional


class Settings:
    """Application settings loaded from environment variables.

    Avoid heavy dependencies; use a minimal loader for now.
    """

    def __init__(self) -> None:
        self.environment: str = os.getenv("ENV", "development")
        self.mapbox_mcp_url: str = os.getenv("MAPBOX_MCP_URL", "")
        self.mapbox_access_token: Optional[str] = os.getenv("MAPBOX_ACCESS_TOKEN")
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
