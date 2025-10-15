from typing import Any, Dict, List


class VisionAgent:
    """Vision agent wrapper (e.g., via LangChain) for solar panel detection."""

    def __init__(self) -> None:
        pass

    def detect_panels_on_tiles(self, tiles: List[bytes]) -> List[Dict[str, Any]]:
        """Return tags with confidence per tile: solar_present/solar_absent/uncertain."""
        raise NotImplementedError
