# Roof Analysis Pipeline

1. **Input Parsing:**  
   - Normalize user location → geocoding with Mapbox  
2. **Image Fetching:**  
   - Generate bounding box → sample 20 coords at zoom 16+  
   - Download 512×512px tiles  
3. **LLM Vision:**  
   - Preprocess with torchvision transforms  
   - Invoke LangChain’s `VisionAgent` for panel detection  
   - Tag results with confidence scores  
4. **Enrichment & Filtering:**  
   - Query ZIP code wealth API  
   - Filter homes >75th percentile and `solar_absent`  
5. **Packaging:**  
   - Format as CSV/JSON, include `address`, `wealth_pct`, `confidence`  
   - Serve via FastAPI
