import os
from functools import lru_cache
from typing import Optional


class Settings:
    """Application settings loaded from environment variables.

    Avoid heavy dependencies; use a minimal loader for now.
    """

    def __init__(self) -> None:
        self.environment: str = os.getenv("ENV", "development")
        self.mapbox_access_token: Optional[str] = os.getenv("MAPBOX_ACCESS_TOKEN")
        self.google_maps_api_key: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")  # Deprecated, kept for backward compatibility
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        # Zillow API configuration
        self.zillow_api_key: Optional[str] = os.getenv("ZILLOW_API_KEY")
        self.zillow_api_base: str = os.getenv("ZILLOW_API_BASE", "https://zillow-com1.p.rapidapi.com")
        self.zillow_rapidapi_host: str = os.getenv("ZILLOW_RAPIDAPI_HOST", "zillow-com1.p.rapidapi.com")
        # Map image defaults
        self.mapbox_style: str = os.getenv("MAPBOX_STYLE", "mapbox/satellite-v9")
        self.mapbox_zoom: int = int(os.getenv("MAPBOX_ZOOM", "20"))
        self.mapbox_image_size: int = int(os.getenv("MAPBOX_IMAGE_SIZE", "512"))
        self.mapbox_country_filter: str = os.getenv("MAPBOX_COUNTRY", "US")
        # Optional marker for static images (e.g., "pin-s+ff0000" for small red pin; set to empty string to disable)
        self.mapbox_marker: str = os.getenv("MAPBOX_MARKER", "pin-s+ff0000")
        # Vision API configuration (using Gemini by default)
        # Use gemini-2.5-flash as default (latest stable, fast and cheap)
        # Will auto-fallback to best available model if not found
        self.vision_model: str = os.getenv("VISION_MODEL", "gemini-2.5-flash")
        self.vision_confidence_threshold: float = float(os.getenv("VISION_CONFIDENCE_THRESHOLD", "0.4"))  # Lowered to include more uncertain properties as leads
        self.vision_timeout_seconds: float = float(os.getenv("VISION_TIMEOUT_SECONDS", "15"))
        # Vision caching to avoid duplicate OpenAI calls for the same image
        self.vision_cache_enabled: bool = os.getenv("VISION_CACHE_ENABLED", "true").lower() in ("1", "true", "yes")
        self.vision_cache_ttl_seconds: int = int(os.getenv("VISION_CACHE_TTL_SECONDS", "3600"))
        # Endpoint defaults
        self.leads_max_properties: int = int(os.getenv("LEADS_MAX_PROPERTIES", "50"))  # Increased to ensure enough properties for filtering


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
