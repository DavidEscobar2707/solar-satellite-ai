from typing import Any, Dict, List, Optional

import logging
import httpx

logger = logging.getLogger(__name__)


class ZillowClient:
    """Zillow property discovery client, adapted for RapidAPI."""

    def __init__(self, *, api_key: str, base_url: str, rapidapi_host: str = "zillow-com1.p.rapidapi.com", timeout_seconds: float = 15.0) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.rapidapi_host = rapidapi_host
        self._http = httpx.Client(timeout=timeout_seconds)

    def close(self) -> None:
        try:
            self._http.close()
        except Exception:
            logger.debug("Failed to close http client", exc_info=True)

    def search_properties(
        self,
        *,
        location: str,
        max_properties: int,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """Return a list of property dicts with at least: address, lat, lng, zpid, price, beds, baths, livingArea."""
        if not self.api_key:
            raise ValueError("ZILLOW_API_KEY not configured")
        if not location:
            return []

        # Build query params based on RapidAPI example
        params = {
            "location": location,
            "status_type": "ForSale",  # Default to for-sale properties
            "home_type": "Houses",     # Default to houses; adjust if needed
            "limit": max_properties,
        }
        if page > 1:
            params["page"] = page
        if filters:
            # Map filters to query params based on Zillow API
            if "minBeds" in filters and filters["minBeds"] is not None:
                params["beds_min"] = filters["minBeds"]
            if "minBaths" in filters and filters["minBaths"] is not None:
                params["baths_min"] = filters["minBaths"]
            if "propertyType" in filters and filters["propertyType"]:
                # Map propertyType to home_type (e.g., "Houses" for SINGLE_FAMILY)
                params["home_type"] = filters["propertyType"][0] if filters["propertyType"] else "Houses"
            if "minPrice" in filters and filters["minPrice"] is not None:
                params["min_price"] = filters["minPrice"]
            if "maxPrice" in filters and filters["maxPrice"] is not None:
                params["max_price"] = filters["maxPrice"]
            if "statusType" in filters and filters["statusType"] is not None:
                params["status_type"] = filters["statusType"]
            if "isNewConstruction" in filters and filters["isNewConstruction"] is not None:
                params["isNewConstruction"] = "1" if filters["isNewConstruction"] else "0"
            if "isAuction" in filters and filters["isAuction"] is not None:
                params["isAuction"] = "1" if filters["isAuction"] else "0"
            if "preForeclosure" in filters and filters["preForeclosure"] is not None:
                params["PreForeclosure"] = "1" if filters["preForeclosure"] else "0"
            if "saleByOwner" in filters and filters["saleByOwner"] is not None:
                params["saleByOwner"] = filters["saleByOwner"]
            if "maxMonthlyCostPayment" in filters and filters["maxMonthlyCostPayment"] is not None:
                params["maxMonthlyCostPayment"] = filters["maxMonthlyCostPayment"]
            if "sqft" in filters and filters["sqft"] is not None:
                params["sqft"] = filters["sqft"]
            if "small" in filters and filters["small"] is not None:
                params["small"] = "1" if filters["small"] else "0"
            if "large" in filters and filters["large"] is not None:
                params["large"] = "1" if filters["large"] else "0"

        headers = {
            "x-rapidapi-host": self.rapidapi_host,
            "x-rapidapi-key": self.api_key,
        }

        # Expanded logging for debugging and comparison with Postman
        logger.info(f"Making RapidAPI request to: {f'{self.base_url}/propertyExtendedSearch'}")
        logger.info(f"Query params: {params}")
        logger.info(f"Headers: {headers}")

        try:
            resp = self._http.get(f"{self.base_url}/propertyExtendedSearch", params=params, headers=headers)

            # Log response details for debugging
            logger.info(f"Response status: {resp.status_code}")
            logger.info(f"Response body (first 1000 chars): {resp.text[:1000]}")

            if resp.status_code in (401, 403):
                logger.error("RapidAPI authentication failed: %s", resp.text)
                raise ValueError("RapidAPI access denied: check ZILLOW_API_KEY and host")
            resp.raise_for_status()
            data = resp.json() or {}
        except httpx.HTTPError as exc:
            logger.error("RapidAPI HTTP error: %s", exc)
            logger.error(f"Request details: URL={resp.request.url if 'resp' in locals() else 'N/A'}, Headers={headers}")
            raise ValueError(f"RapidAPI request failed: {exc}") from exc

        # Parse RapidAPI response (assumes a structure like {"results": [...]})
        # Adjust this based on actual RapidAPI response format (e.g., it might be {"props": [...]})
        results = data.get("props") or data.get("results") or []  # Fallback if key differs
        norm: List[Dict[str, Any]] = []
        for item in results:
            # Normalize fields (RapidAPI might use different keys, e.g., "price" vs "listPrice")
            norm.append(
                {
                    "address": item.get("address") or f"{item.get('streetAddress', '')}, {item.get('city', '')}, {item.get('state', '')} {item.get('zipcode', '')}",
                    "lat": item.get("latitude") or item.get("lat"),
                    "lng": item.get("longitude") or item.get("lng"),
                    "zpid": str(item.get("zpid")) if item.get("zpid") else None,
                    "price": item.get("price") or item.get("listPrice"),
                    "beds": item.get("bedrooms") or item.get("beds"),
                    "baths": item.get("bathrooms") or item.get("baths"),
                    "livingArea": item.get("livingArea") or item.get("sqft"),
                }
            )
        filtered = [p for p in norm if p.get("lat") is not None and p.get("lng") is not None]
        # Respect max_properties even if the upstream API ignores the "limit" param
        if max_properties and max_properties > 0:
            filtered = filtered[:max_properties]
        return filtered


class LeadScorer:
    """Heuristic lead scoring for ranking properties."""

    def score(self, *, price: Optional[float], living_area: Optional[int]) -> float:
        # Normalize heuristics into [0,1]
        p = 0.0
        if price is not None:
            # Map price to [0,1] with soft cap
            p = min(max(price / 2_000_000.0, 0.0), 1.0)
        a = 0.0
        if living_area is not None:
            a = min(max(living_area / 4000.0, 0.0), 1.0)
        return round(0.6 * p + 0.4 * a, 4)
