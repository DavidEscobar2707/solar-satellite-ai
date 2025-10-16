# Functional & Technical Requirements

## Functional
1. **Property Discovery (Zillow):** Given a `location` (city/ZIP), fetch up to `max_properties` residential properties with coordinates and key attributes (price, beds, baths, livingArea).  
2. **Satellite Imagery (Mapbox):** For each property coordinate, retrieve a static satellite tile at zoom ≥18 (default 512×512).  
3. **Solar Detection (OpenAI Vision):** Classify rooftop solar presence per property with confidence. Labels: `solar_present`, `solar_absent`, `uncertain`.  
4. **Lead Scoring & Filtering:** Prioritize likely buyers: absence of solar, price/livingArea heuristics, optional user filters (beds/baths/type).  
5. **Lead Delivery:** Provide `/api/v1/leads` returning ranked list with Zillow, imagery, and vision metadata.

## Technical
- **Backend:** Python ≥3.10, FastAPI  
- **Integrations:**  
  - Zillow API for property search (requires API key + rate limiting)  
  - Mapbox Static Images API using `MAPBOX_ACCESS_TOKEN`  
  - OpenAI Vision (`gpt-4o`/`gpt-4o-mini`) using `OPENAI_API_KEY`  
- **Configuration (.env):**  
  - `ZILLOW_API_KEY`  
  - `MAPBOX_ACCESS_TOKEN`  
  - `OPENAI_API_KEY`  
  - `LEADS_MAX_PROPERTIES` (default 20)  
  - `MAPBOX_DEFAULT_ZOOM` (default 18)  
  - `VISION_MODEL` (default `gpt-4o-mini`)  
  - `VISION_CONFIDENCE_THRESHOLD` (default 0.6)  
- **Constraints:** Respect upstream ToS, robots, and rate limits; implement retries with exponential backoff and jitter.  
- **Testing:** pytest ≥7.0 with ≥80% coverage for Zillow client, Mapbox client, and vision classifier orchestration.  
- **CI/CD:** GitHub Actions for flake8, black, mypy.  
