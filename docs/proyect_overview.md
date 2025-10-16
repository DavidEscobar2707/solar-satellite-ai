# Solar Panel Lead Generator AI

## Vision
Automate lead generation for solar installers by finding residential properties in a target area that likely do not have rooftop solar, prioritizing high-value homes.

## Goals
- Accept any U.S. `location` (city/ZIP)
- Discover properties via Zillow API with coordinates and attributes
- Fetch high-resolution satellite imagery per property via Mapbox
- Detect solar presence using OpenAI Vision (`gpt-4o`/`gpt-4o-mini`)
- Return ranked JSON leads for sales workflows

## Scope
- **Input:** `location` and optional filters (beds, baths, propertyType, max_properties)  
- **Processing:** Zillow property discovery → Mapbox imagery → OpenAI Vision classification → lead scoring  
- **Output:** `POST /api/v1/leads` returning property-level results  

## Success Metrics
- ≥90% agreement on solar presence vs. human labelers  
- <30s end-to-end latency for 20 properties  
- ≥80% vendor satisfaction in pilot  
