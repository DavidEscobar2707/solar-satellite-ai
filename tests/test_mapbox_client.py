from typing import Any, Dict

import pytest

from solar_ai_backend.services.mapbox_client import MapboxClient


class DummyGetResponse:
    def __init__(self, payload: Dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise AssertionError("HTTP error")

    def json(self) -> Dict[str, Any]:
        return self._payload


def test_validate_location_us_success(monkeypatch: pytest.MonkeyPatch) -> None:
    client = MapboxClient(access_token="test-token")

    def fake_get(url: str, params: Dict[str, Any]) -> DummyGetResponse:  # type: ignore[override]
        return DummyGetResponse({
            "features": [
                {"center": [-117.1687, 32.9466], "place_name": "Carmel Valley, San Diego, CA, USA"}
            ]
        })

    monkeypatch.setattr(client._http, "get", fake_get)

    lon, lat = client.validate_location("Carmel Valley, San Diego")
    assert isinstance(lon, float) and isinstance(lat, float)
    assert -180.0 <= lon <= 180.0
    assert -90.0 <= lat <= 90.0


def test_validate_location_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    client = MapboxClient(access_token="test-token")

    def fake_get(url: str, params: Dict[str, Any]) -> DummyGetResponse:  # type: ignore[override]
        return DummyGetResponse({"features": []})

    monkeypatch.setattr(client._http, "get", fake_get)

    with pytest.raises(ValueError):
        client.validate_location("Unknown Place")


def test_get_satellite_images_returns_urls() -> None:
    client = MapboxClient(access_token="test-token")
    urls = client.get_satellite_images((-117.1687, 32.9466), count=3)
    assert len(urls) == 3
    for u in urls:
        assert isinstance(u, str) and u.startswith("https://api.mapbox.com/styles/v1/")


