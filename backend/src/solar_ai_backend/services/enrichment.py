from typing import Any, Dict, List, Optional

import logging
import httpx

logger = logging.getLogger(__name__)


class ZillowClient:
    """Zillow property discovery client, adapted for RapidAPI."""

    def __init__(self, *, api_key: str, base_url: str, rapidapi_host: str = "zllw-working-api.p.rapidapi.com", timeout_seconds: float = 15.0) -> None:
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

        # Build query params based on new RapidAPI Zillow API
        params = {
            "location": location,
            "page": page,
            "sortOrder": "Homes_for_you",
            "listingStatus": "Sold",  # Default to sold properties as per example
            "bed_min": "No_Min",
            "bed_max": "No_Max",
            "bathrooms": "Any",
            "homeType": "Houses,Townhomes",
            "maxHOA": "Any",
            "listingType": "By_Agent",
            "listingTypeOptions": "Agent listed,New Construction,Fore-closures,Auctions",
            "parkingSpots": "Any",
            "mustHaveBasement": "No",
            "daysOnZillow": "Any",
            "soldInLast": "Any",
        }

        # Apply default price range for wealthy neighborhoods if no filters provided
        if not filters:
            params["listPriceRange"] = "min:500000,max:1000000"  # Default price range
        if filters:
            # Map filters to new API parameter format
            # Price filters
            min_price = None
            max_price = None

            if "minPrice" in filters and filters["minPrice"] is not None:
                min_price = filters["minPrice"]
            if "maxPrice" in filters and filters["maxPrice"] is not None:
                max_price = filters["maxPrice"]
            if "priceRange" in filters and filters["priceRange"]:
                try:
                    rng = str(filters["priceRange"]).replace(" ", "")
                    lo, hi = rng.split("-")
                    if lo and not min_price:
                        min_price = int(lo)
                    if hi and not max_price:
                        max_price = int(hi)
                except Exception:
                    logger.debug("Ignoring malformed priceRange: %s", filters.get("priceRange"))

            if min_price is not None or max_price is not None:
                min_str = f"min:{min_price}" if min_price else ""
                max_str = f"max:{max_price}" if max_price else ""
                if min_str and max_str:
                    params["listPriceRange"] = f"{min_str},{max_str}"
                elif min_str:
                    params["listPriceRange"] = min_str
                elif max_str:
                    params["listPriceRange"] = max_str

            # Bedrooms
            if "minBeds" in filters and filters["minBeds"] is not None:
                params["bed_min"] = str(filters["minBeds"])
            if "maxBeds" in filters and filters["maxBeds"] is not None:
                params["bed_max"] = str(filters["maxBeds"])

            # Bathrooms
            if "minBaths" in filters and filters["minBaths"] is not None:
                params["bathrooms"] = str(filters["minBaths"])

            # Property type
            if "propertyType" in filters and filters["propertyType"]:
                if isinstance(filters["propertyType"], list):
                    # Map property types to API format
                    type_mapping = {
                        "SINGLE_FAMILY": "Houses",
                        "CONDO": "Condos",
                        "TOWNHOUSE": "Townhomes",
                        "MULTI_FAMILY": "Multi-family",
                        "LAND": "Lots",
                        "OTHER": "Other"
                    }
                    mapped_types = []
                    for pt in filters["propertyType"]:
                        mapped = type_mapping.get(pt, pt)
                        if mapped not in mapped_types:
                            mapped_types.append(mapped)
                    if mapped_types:
                        params["homeType"] = ",".join(mapped_types)
                else:
                    params["homeType"] = str(filters["propertyType"])

            # Listing status
            if "statusType" in filters and filters["statusType"] is not None:
                status_mapping = {
                    "ForSale": "For Sale",
                    "RecentlySold": "Sold",
                    "ForRent": "For Rent"
                }
                params["listingStatus"] = status_mapping.get(filters["statusType"], filters["statusType"])

            # Keywords (if supported by this endpoint)
            if "keywords" in filters and filters["keywords"]:
                # Note: This endpoint might not support keywords, but we'll include it for compatibility
                params["keywords"] = filters["keywords"]

        headers = {
            "x-rapidapi-host": self.rapidapi_host,
            "x-rapidapi-key": self.api_key,
        }

        # Expanded logging for debugging and comparison with Postman
        logger.info(f"Making RapidAPI request to: {f'{self.base_url}/search/byaddress'}")
        logger.info(f"Query params: {params}")
        logger.info(f"Headers: {headers}")

        try:
            resp = self._http.get(f"{self.base_url}/search/byaddress", params=params, headers=headers)

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
        # Parse new RapidAPI response structure with searchResults
        search_results = data.get("searchResults") or {}
        results = []
        if isinstance(search_results, dict):
            # searchResults is an object with numeric keys like "0", "1", etc.
            for key, result in search_results.items():
                if isinstance(result, dict) and "property" in result:
                    results.append(result["property"])
        elif isinstance(search_results, list):
            # Fallback in case it's an array
            results = search_results
        norm: List[Dict[str, Any]] = []
        for item in results:
            # Normalize fields based on new API structure
            # Extract location data
            location_data = item.get("location", {})
            address_data = item.get("address", {})

            # Extract listing data
            listing_data = item.get("listing", {})

            # Build address string
            address_parts = []
            if address_data.get("streetAddress"):
                address_parts.append(address_data["streetAddress"])
            city_state_zip = []
            if address_data.get("city"):
                city_state_zip.append(address_data["city"])
            if address_data.get("state"):
                city_state_zip.append(address_data["state"])
            if address_data.get("zipcode"):
                city_state_zip.append(address_data["zipcode"])
            if city_state_zip:
                address_parts.append(", ".join(city_state_zip))

            norm.append(
                {
                    "address": " ".join(address_parts) if address_parts else item.get("address", ""),
                    "lat": location_data.get("latitude"),
                    "lng": location_data.get("longitude"),
                    "zpid": str(item.get("zpid")) if item.get("zpid") else None,
                    "price": listing_data.get("price", {}).get("value") or item.get("price"),
                    "beds": item.get("bedrooms"),
                    "baths": item.get("bathrooms"),
                    "livingArea": item.get("livingArea"),
                    "lotSize": item.get("lotSizeWithUnit", {}).get("lotSize") or item.get("lotSize"),
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
