# System Architecture & Folder Layout

flowchart TD
A[User Input] --> B[Mapbox Image Retrieval]
B --> C[LangChain Vision Agent]
C --> D[Wealth Enrichment API]
D --> E[Lead Filter & Scoring]
E --> F[FastAPI /leads Endpoint]

text

## Folder Layout

solar-satellite-ai/
└── backend/
├── src/solar_ai_backend/
│ ├── api/ # FastAPI routers
│ ├── services/ # Mapbox fetch, LLM inference, enrichment
│ ├── schemas/ # Pydantic models
│ ├── core/ # LangChain context managers
│ ├── models/ # Vision & data classes
│ └── config.py # Env & constants loader
├── tests/ # Unit & integration tests
├── pyproject.toml
└── .cursor/rules/ # Project‐wide coding & context rules