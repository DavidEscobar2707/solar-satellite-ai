# System Architecture & Folder Layout

flowchart TD
 A[User Input: locality/city/ZIP] --> Z[Zillow API: property search]
 Z --> M[Mapbox Static Images: per-property satellite tile]
 M --> V[OpenAI Vision: solar panel detection]
 V --> L[Lead Filter & Scoring]
 L --> E[FastAPI /api/v1/leads Endpoint]

text

## Folder Layout

solar-satellite-ai/
└── backend/
├── src/solar_ai_backend/
│ ├── api/ # FastAPI routers
│ ├── services/ # Zillow ingestion, Mapbox imagery, OpenAI vision, enrichment
│ ├── schemas/ # Pydantic models
│ ├── core/ # Inference/runtime utilities
│ ├── models/ # Vision & data classes
│ └── config.py # Env & constants loader
├── tests/ # Unit & integration tests
├── pyproject.toml
└── .cursor/rules/ # Project‐wide coding & context rules