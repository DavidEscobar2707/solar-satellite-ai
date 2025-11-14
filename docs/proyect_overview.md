# BackyardLeadAI – Backyard Lead Generator AI

## Vision
Automate lead generation for landscaping companies by finding residential properties in a target area that have undeveloped or underused backyards, prioritizing high‑value homes with strong outdoor improvement potential.

## Goals
- Accept any U.S. `location` (city/ZIP)
- Discover residential properties via Zillow API with coordinates and attributes
- Fetch high‑resolution satellite imagery per property via an imagery provider (e.g., Google Maps Static)
- Detect backyard status (undeveloped vs. landscaped) using OpenAI Vision (`gpt-4o`/`gpt-4o-mini`)
- Return ranked JSON leads representing high‑value landscaping opportunities

## Scope
- **Input:** `location` and optional filters (beds, baths, propertyType, max_properties)  
- **Processing:** Zillow property discovery → satellite imagery → OpenAI Vision backyard classification → lead scoring  
- **Output:** `POST /api/v1/leads` returning property‑level results with backyard status and lead score  

## Success Metrics
- ≥90% agreement on backyard status (undeveloped / developed) vs. human labelers  
- <30s end‑to‑end latency for 20 properties  
- ≥80% landscaping customer satisfaction in pilot  
