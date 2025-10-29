import logging
from typing import List, Optional, Tuple

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


class GoogleMapsClient:
    """Client for Google Maps APIs (Static and Geocoding) to fetch satellite imagery and validate locations."""

    def __init__(self, *, api_key: str, timeout_seconds: float = 15.0) -> None:
        self.api_key = api_key
        self.geocoding_base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.static_base_url = "https://maps.googleapis.com/maps/api/staticmap"
        self._http = httpx.Client(timeout=timeout_seconds)

    def close(self) -> None:
        """Close the HTTP client."""
        try:
            self._http.close()
        except Exception:
            logger.debug("Failed to close HTTP client", exc_info=True)

    def build_static_image_url(
        self,
        *,
        longitude: float,
        latitude: float,
        zoom: int = 20,
        width_px: int = 512,
        height_px: int = 512,
        maptype: str = "satellite",
        with_marker: bool = True,
    ) -> str:
        """Build a Google Maps Static Image URL for satellite view of a property."""
        # Google Maps Static API URL format
        url = (
            f"{self.static_base_url}?"
            f"center={latitude},{longitude}&"
            f"zoom={zoom}&"
            f"size={width_px}x{height_px}&"
            f"maptype={maptype}&"
            f"key={self.api_key}"
        )
        if with_marker:
            # Add a default marker at the center coordinates
            url = f"{url}&markers={latitude},{longitude}"
        logger.debug(f"Google Maps Static Image URL: {url}")
        return url

    def validate_location(self, location: str) -> Tuple[float, float]:
        """Geocode a location string to longitude and latitude."""
        params = {"address": location, "key": self.api_key}
        try:
            resp = self._http.get(self.geocoding_base_url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "OK" and data.get("results"):
                result = data["results"][0]
                geometry = result.get("geometry", {})
                location_data = geometry.get("location", {})
                return location_data.get("lng"), location_data.get("lat")
            else:
                raise ValueError(f"Geocoding failed: {data.get('status')}")
        except httpx.HTTPError as e:
            logger.error(f"Geocoding HTTP error: {e}")
            raise ValueError(f"Geocoding failed: {e}")

    def get_satellite_image_url(
        self,
        *,
        longitude: float,
        latitude: float,
        zoom: int = 20,
        width_px: int = 512,
        height_px: int = 512,
        with_marker: bool = True,
    ) -> str:
        """Get the URL for a satellite image of the given coordinates."""
        return self.build_static_image_url(
            longitude=longitude,
            latitude=latitude,
            zoom=zoom,
            width_px=width_px,
            height_px=height_px,
            with_marker=with_marker,
        )

    def get_satellite_images(
        self,
        coordinates: Tuple[float, float],
        count: int = 20,
        *,
        zoom: Optional[int] = None,
        width_px: Optional[int] = None,
        height_px: Optional[int] = None,
        with_marker: bool = True,
    ) -> List[str]:
        """Return a list of static satellite image URLs for the given center.

        Mirrors the Mapbox client's interface used by routes for easy swap.
        """
        if count <= 0:
            return []

        lon, lat = coordinates
        settings = get_settings()
        z = zoom if zoom is not None else settings.mapbox_zoom
        w = width_px if width_px is not None else settings.mapbox_image_size
        h = height_px if height_px is not None else settings.mapbox_image_size

        url = self.get_satellite_image_url(
            longitude=lon,
            latitude=lat,
            zoom=z,
            width_px=w,
            height_px=h,
            with_marker=with_marker,
        )

        # For now, return the same centered image URL repeated 'count' times.
        # This matches previous Mapbox behavior and keeps route logic unchanged.
        return [url for _ in range(count)]
