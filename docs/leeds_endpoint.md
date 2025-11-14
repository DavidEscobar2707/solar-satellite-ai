# `/api/v1/leads` Endpoint

Creates and returns landscaping sales leads using Zillow → satellite imagery → OpenAI Vision to find homes with undeveloped or underused backyards.

## `POST` `/api/v1/leads`

Request body:
```
{
  "location": "San Diego, CA",
  "max_properties": 50,          // optional, default 20
  "zillow_filters": {            // optional; passed to Zillow search
    "minBeds": 3,
    "minBaths": 2,
    "propertyType": ["SINGLE_FAMILY"]
  },
  "imagery": {                   // optional; imagery provider params
    "zoom": 18,
    "size": { "w": 512, "h": 512 }
  },
  "vision": {                    // optional; OpenAI Vision params
    "model": "gpt-4o-mini",
    "confidence_threshold": 0.6
  }
}
```

Response body:
```
{
  "location": "San Diego, CA",
  "count": 27,
  "leads": [
    {
      "address": "123 Main St, San Diego, CA 92130",
      "coordinates": { "lat": 32.9466, "lng": -117.1687 },
      "zillow": {
        "zpid": "1234567",
        "price": 1850000,
        "beds": 4,
        "baths": 3,
        "livingArea": 2650,
        "lotSize": 6500
      },
      "imagery": {
        "image_url": "https://maps.googleapis.com/maps/api/staticmap?...",
        "zoom": 20,
        "size": { "w": 512, "h": 512 }
      },
      "vision": {
        "backyard_status": "undeveloped",      // undeveloped | partially_developed | fully_landscaped | uncertain
        "backyard_confidence": 0.82,
        "notes": "Large, mostly bare backyard with visible dirt/grass and no pool or hardscape.",
        "model": "gpt-4o-mini"
      },
      "lead_score": 0.86                      // 0–1, higher = better landscaping opportunity
    }
  ]
}
```

### Processing
1. Resolve `location` to city/ZIP context for Zillow search.
2. Query Zillow API with pagination for property variety (pages 1-5, up to `max_properties` per page).
3. For each property, fetch a satellite tile (e.g., from Google Maps Static API).
4. Run OpenAI Vision to classify backyard status and identify undeveloped or underused outdoor space.
5. Score and filter: prioritize properties with `backyard_status="undeveloped"` or `partially_developed` ordered by landscaping potential.

### Errors
- `400` invalid input
- `502` Zillow/imagery provider/OpenAI upstream failure
- `500` internal error
