# Functional & Technical Requirements

## Functional
1. **Location Validation:** Must parse and validate U.S. place names.  
2. **Image Retrieval:** Retrieve 20 unique satellite images at zoom ≥16.  
3. **Panel Detection:** Classify each roof as `solar_present`, `solar_absent`, or `uncertain`.  
4. **Wealth Filtering:** Query external API for ZIP‐level wealth percentiles; select ≥75th percentile.  
5. **Lead Delivery:** Expose a FastAPI `/leads` endpoint returning filtered results.

## Technical
- **Backend:** Python ≥3.10, FastAPI, LangChain  
- **Mapping:** Mapbox API v4 with API key from `.env`  
- **Enrichment:** U.S. Census wealth API  
- **Testing:** pytest ≥7.0 with ≥80% coverage  
- **CI/CD:** GitHub Actions for linting (flake8), formatting (black), type checks (mypy)  
