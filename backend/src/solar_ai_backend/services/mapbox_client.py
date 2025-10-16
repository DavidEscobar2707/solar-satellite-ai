from typing import Any, Dict, List, Optional, Tuple

import logging
import httpx
import urllib.parse
from ..config import get_settings


logger = logging.getLogger(__name__)


class MapboxClient:
    """Direct Mapbox REST API client (Geocoding + Static Images)."""

    def __init__(
        self,
        *,
        access_token: str,
        image_size_px: int = 512,
        style: str = "mapbox/satellite-v9",
        country_filter: str = "US",
        timeout_seconds: float = 10.0,
    ) -> None:
        self.base_url = "https://api.mapbox.com"
        self.access_token = access_token
        self.image_size_px = image_size_px
        self.style = style
        self.country_filter = country_filter
        self.timeout_seconds = timeout_seconds

        self._http = httpx.Client(timeout=self.timeout_seconds)
        
        # Validate token presence
        if not access_token:
            logger.warning("MapboxClient initialized with empty access_token")

    def validate_location(self, location: str) -> Tuple[float, float]:
        """Validate and geocode a free-form US location string to coordinates.
        
        Returns (longitude, latitude).
        Raises ValueError if the location cannot be validated or is not in the US.
        """
        if not self.access_token:
            raise ValueError("Mapbox access token is required")
            
        if not location:
            raise ValueError("Location cannot be empty")
            
        # Use urllib.parse.quote for proper URL encoding
        encoded = urllib.parse.quote(location, safe="")
        url = f"{self.base_url}/geocoding/v5/mapbox.places/{encoded}.json"
        params = {
            "access_token": self.access_token,
            "limit": 1,
            "country": self.country_filter.lower()
        }
        
        try:
            response = self._http.get(url, params=params)
            
            if response.status_code in (401, 403):
                logger.error(f"Mapbox authorization error: {response.text}")
                raise ValueError("Mapbox access denied: check MAPBOX_ACCESS_TOKEN")
                
            response.raise_for_status()
            data = response.json()
            
        except httpx.HTTPError as exc:
            logger.error(f"HTTP error during Mapbox geocoding: {exc}")
            raise ValueError(f"Failed to validate location: {str(exc)}") from exc

        features = data.get("features") or []
        if not features:
            raise ValueError("Location not found")
            
        first = features[0]
        coords = first.get("center") or []
        
        if len(coords) < 2:
            raise ValueError("Invalid geocoding response")
            
        lon, lat = float(coords[0]), float(coords[1])
        
        # Check country code if available
        if self.country_filter:
            place_type = first.get("place_type", [])
            context = first.get("context", [])
            country_code = None
            
            # Try to extract country code from context
            for ctx in context:
                if ctx.get("id", "").startswith("country."):
                    country_code = ctx.get("short_code", "").upper()
                    break
            
            # If we found a country code and it doesn't match our filter
            if country_code and country_code != self.country_filter.upper():
                raise ValueError(f"Only {self.country_filter} locations are supported")

        return lon, lat

    def get_satellite_images(self, coordinates: Tuple[float, float], count: int = 20) -> List[str]:
        """Return a list of static satellite image URLs for the given center."""
        if count <= 0:
            return []
            
        lon, lat = coordinates
        urls: List[str] = []
        
        for _ in range(count):
            url = (
                f"{self.base_url}/styles/v1/{self.style}/static/{lon},{lat},{get_settings().mapbox_zoom},0,0/{self.image_size_px}x{self.image_size_px}"
                f"?access_token={self.access_token}"
            )
            urls.append(url)
            
        return urls
    
    def build_static_image_url(
        self,
        *,
        longitude: float,
        latitude: float,
        zoom: Optional[int] = None,
        width_px: Optional[int] = None,
        height_px: Optional[int] = None,
        marker: Optional[str] = None,
    ) -> str:
        """Build a Mapbox Static Image URL for a single property coordinate, with optional marker overlay."""
        z = zoom if zoom is not None else get_settings().mapbox_zoom
        w = width_px if width_px is not None else self.image_size_px
        h = height_px if height_px is not None else self.image_size_px
        # Use provided marker or default from settings
        marker_overlay = marker if marker is not None else get_settings().mapbox_marker

        # Base URL without marker
        base_url = (
            f"{self.base_url}/styles/v1/{self.style}/static/"
            f"{longitude},{latitude},{z},0,0/{w}x{h}?access_token={self.access_token}"
        )
        logger.debug(f"Base URL without marker: {base_url}")

        # Add marker overlay if specified (non-empty)
        if marker_overlay:
            # Insert marker before the coordinates in the path with proper separator
            url = base_url.replace(
                f"{longitude},{latitude},{z},0,0",
                f"{marker_overlay}({longitude},{latitude})/{longitude},{latitude},{z},0,0"
            )
            logger.debug(f"Final URL with marker: {url}")
        else:
            url = base_url
            logger.debug(f"No marker added, using base URL: {url}")

        return url
        
    def close(self) -> None:
        """Close the HTTP client."""
        try:
            self._http.close()
        except Exception:  # pragma: no cover
            logger.debug("Failed to close http client", exc_info=True)