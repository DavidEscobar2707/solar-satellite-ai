# Functional & Technical Requirements

## Functional
1. **Property Discovery (Zillow):** Given a `location` (city/ZIP), fetch up to `max_properties` residential properties with coordinates and key attributes (price, beds, baths, livingArea, lotSize when available).  
2. **Satellite Imagery (Imagery Provider):** For each property coordinate, retrieve a static satellite tile at zoom ≥18 (default 512×512).  
3. **Backyard Status Detection (Google Gemini Vision):** Classify backyard development status per property with confidence. Labels: `undeveloped`, `partially_developed`, `fully_landscaped`, `uncertain`.  
4. **Lead Scoring & Filtering (Landscaping):** Prioritize likely landscaping buyers: large or underused backyards, price/livingArea/lotSize heuristics, optional user filters (beds/baths/type).  
5. **Lead Delivery:** Provide `/api/v1/leads` returning a ranked list with Zillow data, imagery, backyard classification, and lead scoring metadata.

## Technical
- **Backend:** Python ≥3.10, FastAPI  
- **Integrations:**  
  - Zillow API for property search (requires API key + rate limiting)  
  - Imagery API for static satellite images (e.g., Google Maps Static, Mapbox)  
  - Google Gemini Vision (`gemini-1.5-flash`) using `GEMINI_API_KEY`  
- **Configuration (.env):**  
  - `ZILLOW_API_KEY`  
  - `IMAGERY_API_KEY` (e.g., Google Maps or Mapbox)  
  - `GEMINI_API_KEY` (Google Gemini API key)  
  - `LEADS_MAX_PROPERTIES` (default 20)  
  - `IMAGERY_DEFAULT_ZOOM` (default 18)  
  - `VISION_MODEL` (default `gemini-1.5-flash`)  
  - `VISION_CONFIDENCE_THRESHOLD` (default 0.6)  
- **Constraints:** Respect upstream ToS, robots, and rate limits; implement retries with exponential backoff and jitter.  
- **Testing:** pytest ≥7.0 with ≥80% coverage for Zillow client, Mapbox client, and vision classifier orchestration.  
- **CI/CD:** GitHub Actions for flake8, black, mypy.  
