from fastapi import FastAPI
from fastapi import status

from .schemas.models import LeadsRequest, LeadsResponse

app = FastAPI(title="Solar AI Backend", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/leads", response_model=LeadsResponse, status_code=status.HTTP_201_CREATED)
def create_leads(request: LeadsRequest) -> LeadsResponse:
    # TODO: Wire Mapbox, Vision agent, and enrichment services
    return LeadsResponse(leads=[], count=0)
