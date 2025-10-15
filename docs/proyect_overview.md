# Solar Panel Lead Generator AI

## Vision
Automate satellite‐based lead generation for solar panel installers by identifying wealthy U.S. neighborhoods without existing rooftop panels.

## Goals
- Accept any U.S. location (e.g., Carmel Valley, San Diego)
- Fetch 20 high‐resolution satellite images via Mapbox
- Analyze roofs with a LangChain vision agent to detect solar panels
- Enrich results with wealth percentile data
- Deliver CSV/JSON lead lists of affluent homes lacking solar panels

## Scope
- **Input:** User location string  
- **Processing:** Mapbox image retrieval → LLM vision analysis → data enrichment  
- **Output:** `/leads` endpoint returning qualified homes  

## Success Metrics
- ≥90% accuracy in panel detection  
- Lead lists generated in <30s per request  
- 80% user satisfaction from pilot vendors  
