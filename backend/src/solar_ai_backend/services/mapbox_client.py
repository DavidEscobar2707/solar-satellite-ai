from typing import Any, Dict, List, Optional, Tuple


class MapboxClient:
    """Thin client around Mapbox APIs or the MCP Mapbox service.

    This class is a placeholder; wire actual HTTP/MCP calls later.
    """

    def __init__(self, base_url: str, access_token: Optional[str] = None) -> None:
        self.base_url = base_url
        self.access_token = access_token

    def geocode_location(self, location_text: str) -> Dict[str, Any]:
        """Resolve user-provided location text into a canonical place or bbox."""
        raise NotImplementedError

    def sample_coordinates(self, bbox: Tuple[float, float, float, float], *, n: int = 20) -> List[Tuple[float, float]]:
        """Sample N coordinate pairs within a bounding box."""
        raise NotImplementedError

    def fetch_satellite_tiles(self, coordinates: List[Tuple[float, float]], *, zoom: int = 16, size_px: int = 512) -> List[bytes]:
        """Fetch raster tiles for each coordinate. Returns raw image bytes."""
        raise NotImplementedError
