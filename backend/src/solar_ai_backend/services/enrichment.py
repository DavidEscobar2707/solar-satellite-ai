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
        
        # Apply default filters for wealthy neighborhoods if no filters provided
        if not filters:
            params["min_price"] = 1500000  # Default minimum: $1.5M for wealthy neighborhoods
            params["max_price"] = 5000000  # Default maximum: $5M
            # Note: keywords filter removed as it may not be supported by Zillow API
        
        if page > 1:
            params["page"] = page
        if filters:
            # Map filters to query params based on Zillow API
            def _bool_to_str(v: Any) -> str:
                if isinstance(v, bool):
                    return "1" if v else "0"
                return str(v)

            if "minBeds" in filters and filters["minBeds"] is not None:
                params["beds_min"] = filters["minBeds"]
            if "minBaths" in filters and filters["minBaths"] is not None:
                params["baths_min"] = filters["minBaths"]
            if "propertyType" in filters and filters["propertyType"]:
                # Map propertyType to home_type (e.g., "Houses" for SINGLE_FAMILY)
                params["home_type"] = filters["propertyType"][0] if filters["propertyType"] else "Houses"
            # Price filters and optional "priceRange" shorthand (e.g., "200000-500000")
            if "minPrice" in filters and filters["minPrice"] is not None:
                params["min_price"] = filters["minPrice"]
            if "maxPrice" in filters and filters["maxPrice"] is not None:
                params["max_price"] = filters["maxPrice"]
            # Keywords filter - only add if provided (may not be supported by all Zillow API endpoints)
            if "keywords" in filters and filters["keywords"]:
                # Note: Some Zillow API endpoints may not support keywords filter
                # If it causes issues, we can remove it or make it optional
                params["keywords"] = filters["keywords"]
            if "priceRange" in filters and filters["priceRange"]:
                try:
                    rng = str(filters["priceRange"]).replace(" ", "")
                    lo, hi = rng.split("-")
                    if lo:
                        params["min_price"] = int(lo)
                    if hi:
                        params["max_price"] = int(hi)
                except Exception:
                    logger.debug("Ignoring malformed priceRange: %s", filters.get("priceRange"))
            if "statusType" in filters and filters["statusType"] is not None:
                params["status_type"] = filters["statusType"]
            if "isNewConstruction" in filters and filters["isNewConstruction"] is not None:
                params["isNewConstruction"] = _bool_to_str(filters["isNewConstruction"])  # API expects 1/0
            if "isAuction" in filters and filters["isAuction"] is not None:
                params["isAuction"] = _bool_to_str(filters["isAuction"])  # API expects 1/0
            if "preForeclosure" in filters and filters["preForeclosure"] is not None:
                params["PreForeclosure"] = _bool_to_str(filters["preForeclosure"])  # API expects 1/0
            # FSBO (For Sale By Owner) / sale by agent flags
            if "saleByOwner" in filters and filters["saleByOwner"] is not None:
                params["saleByOwner"] = str(filters["saleByOwner"]).lower() if isinstance(filters["saleByOwner"], bool) else filters["saleByOwner"]
            if "saleByAgent" in filters and filters["saleByAgent"] is not None:
                params["saleByAgent"] = str(filters["saleByAgent"]).lower() if isinstance(filters["saleByAgent"], bool) else filters["saleByAgent"]
            # Other listings tab toggle
            if "otherListings" in filters and filters["otherListings"] is not None:
                params["otherListings"] = _bool_to_str(filters["otherListings"])  # API expects 1/0
            if "maxMonthlyCostPayment" in filters and filters["maxMonthlyCostPayment"] is not None:
                params["maxMonthlyCostPayment"] = filters["maxMonthlyCostPayment"]
            if "sqft" in filters and filters["sqft"] is not None:
                params["sqft"] = filters["sqft"]
            if "small" in filters and filters["small"] is not None:
                params["small"] = _bool_to_str(filters["small"])  # API expects 1/0
            if "large" in filters and filters["large"] is not None:
                params["large"] = _bool_to_str(filters["large"])  # API expects 1/0
            # Keywords filter (e.g., "backyard" for properties with backyard mentions)
            if "keywords" in filters and filters["keywords"]:
                params["keywords"] = filters["keywords"]
            # Optional spatial alternatives to location (Zillow supports one of location | coordinates | polygon)
            if "coordinates" in filters and filters["coordinates"]:
                params["coordinates"] = filters["coordinates"]  # "lon lat,diameter" (miles)
            if "polygon" in filters and filters["polygon"]:
                params["polygon"] = filters["polygon"]  # "lon lat,lon1 lat1,...,lon lat" (closed)

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
                    "lotSize": item.get("lotSize") or item.get("lotSizeSqFt") or item.get("lotAreaValue"),
                }
            )
        filtered = [p for p in norm if p.get("lat") is not None and p.get("lng") is not None]
        # Respect max_properties even if the upstream API ignores the "limit" param
        if max_properties and max_properties > 0:
            filtered = filtered[:max_properties]
        return filtered


class LeadScorer:
    """Heuristic lead scoring for ranking properties based on landscaping potential."""

    def score(self, *, price: Optional[float], living_area: Optional[int], lot_size: Optional[int] = None) -> float:
        # Normalize heuristics into [0,1] for landscaping leads
        # Prioritize properties with good price, decent living area, and larger lots
        p = 0.0
        if price is not None:
            # Map price to [0,1] with soft cap (higher value homes = better landscaping potential)
            p = min(max(price / 2_000_000.0, 0.0), 1.0)
        a = 0.0
        if living_area is not None:
            # Larger homes often have more landscaping potential
            a = min(max(living_area / 4000.0, 0.0), 1.0)
        l = 0.0
        if lot_size is not None:
            # Larger lots = more backyard space for landscaping
            # Normalize assuming typical lot sizes range from 5000-15000 sqft
            l = min(max((lot_size - 3000) / 12000.0, 0.0), 1.0)
        
        # Weight: price 40%, lot size 40%, living area 20% (lot size is key for landscaping)
        if lot_size is not None:
            return round(0.4 * p + 0.4 * l + 0.2 * a, 4)
        else:
            # Fallback if lot_size not available
            return round(0.6 * p + 0.4 * a, 4)
