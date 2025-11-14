# System Architecture & Folder Layout

flowchart TD
 A[User Input: locality/city/ZIP] --> Z[Zillow API: property search]
 Z --> M[Imagery API: per-property satellite tile]
 M --> V[OpenAI Vision: backyard analysis]
 V --> L[Lead Filter & Scoring (landscaping potential)]
 L --> E[FastAPI /api/v1/leads Endpoint]

text

## Folder Layout

backyardleadai/
└── backend/
├── src/backyard_ai_backend/
│ ├── api/ # FastAPI routers
│ ├── services/ # Zillow ingestion, imagery retrieval, OpenAI Vision backyard classifier, enrichment
│ ├── schemas/ # Pydantic models
│ ├── core/ # Inference/runtime utilities
│ ├── models/ # Vision & data classes (backyard status, lead scoring)
│ └── config.py # Env & constants loader
├── tests/ # Unit & integration tests
├── pyproject.toml
└── .cursor/rules/ # Project‐wide coding & context rules