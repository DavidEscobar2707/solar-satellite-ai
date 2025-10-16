# Roof Analysis & Lead Generation Pipeline

1. **Property Discovery (Zillow):**  
   - Resolve `location` (city/ZIP) to Zillow search context  
   - Request up to `max_properties` with coordinates and attributes (zpid, price, beds, baths, livingArea)  
2. **Satellite Imagery (Mapbox):**  
   - For each property coordinate, request Static Images tile 512×512 at zoom ≥18  
   - Persist pre-signed URLs or bytes (as configured)  
3. **OpenAI Vision Classification:**  
   - Prompt model (e.g., `gpt-4o-mini`) with a concise instruction: detect rooftop solar panels  
   - Return `{ solar_present: boolean | null, confidence: number }`  
4. **Lead Scoring & Filtering:**  
   - Exclude `solar_present=true`; keep `false` or `null` with low confidence  
   - Score using price, livingArea, optional user filters; sort desc  
5. **Output Packaging:**  
   - Produce JSON leads with `address`, `coordinates`, Zillow attributes, Mapbox URL, vision result, and `lead_score`  
   - Serve via `POST /api/v1/leads`
