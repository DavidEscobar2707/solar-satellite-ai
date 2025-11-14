# Backyard Analysis & Lead Generation Pipeline

1. **Property Discovery (Zillow):**  
   - Resolve `location` (city/ZIP) to Zillow search context  
   - Request up to `max_properties` with coordinates and attributes (zpid, price, beds, baths, livingArea, lotSize when available)  
2. **Satellite Imagery (Imagery Provider):**  
   - For each property coordinate, request a static satellite tile 512×512 at zoom ≥18  
   - Persist pre‑signed URLs or bytes (as configured)  
3. **OpenAI Vision Backyard Classification:**  
   - Prompt model (e.g., `gpt-4o-mini`) with concise instructions to analyze the backyard area and classify development status  
   - Return an object like:  
     - `backyard_status`: `undeveloped` | `partially_developed` | `fully_landscaped` | `uncertain`  
     - `backyard_confidence`: 0–1  
     - `notes`: short explanation (e.g., “large bare dirt area; no pool or patio”)  
4. **Lead Scoring & Filtering (Landscaping Potential):**  
   - Prioritize properties with `backyard_status` in {`undeveloped`, `partially_developed`}  
   - Incorporate price, livingArea, lotSize, and optional user filters (beds/baths/type) into a composite `lead_score` (0–1)  
   - Optionally include `fully_landscaped` or `uncertain` as lower‑priority leads when inventory is limited  
5. **Output Packaging:**  
   - Produce JSON leads with `address`, `coordinates`, Zillow attributes, imagery URL, backyard classification result, and `lead_score`  
   - Serve via `POST /api/v1/leads`
