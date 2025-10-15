from typing import Any, Dict, List, Optional


class EnrichmentService:
    """External enrichment (e.g., US Census wealth percentile) placeholder."""

    def __init__(self) -> None:
        pass

    def enrich(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Augment detection records with wealth percentile and address metadata."""
        raise NotImplementedError
