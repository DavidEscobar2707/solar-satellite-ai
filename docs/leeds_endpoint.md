# `/api/v1/leads` Endpoint

Creates and returns solar sales leads using Zillow → Mapbox → OpenAI Vision.

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
  "imagery": {                   // optional; Mapbox imagery params
    "zoom": 18,
    "size": { "w": 512, "h": 512 }
  },
  "vision": {                    // optional; OpenAI vision params
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
        "livingArea": 2650
      },
      "imagery": {
        "mapbox_url": "https://api.mapbox.com/styles/v1/...",
        "zoom": 18,
        "size": { "w": 512, "h": 512 }
      },
      "vision": {
        "solar_present": false,
        "confidence": 0.82,
        "model": "gpt-4o-mini"
      },
      "lead_score": 0.77
    }
  ]
}
```

### Processing
1. Resolve `location` to city/ZIP context for Zillow search.
2. Query Zillow API for property coordinates and metadata.
3. For each property, fetch a satellite tile from Mapbox.
4. Run OpenAI Vision to classify rooftop solar presence.
5. Score and filter: return properties with `solar_present=false` ordered by score.

### Errors
- `400` invalid input
- `502` Zillow/Mapbox/OpenAI upstream failure
- `500` internal error
