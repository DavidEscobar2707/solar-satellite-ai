from typing import Optional, List

from pydantic import BaseModel, Field


class LeadsRequest(BaseModel):
    """Request payload for generating leads.

    location: Free-form text such as a city, neighborhood, or ZIP code.
    limit: Maximum number of candidate homes to return.
    """

    location: str = Field(..., description="User-provided location text (e.g., 'Carmel Valley, San Diego')")
    limit: int = Field(default=20, ge=1, le=500, description="Maximum number of results to return")


class Lead(BaseModel):
    address: Optional[str] = Field(default=None, description="Street address if available")
    latitude: Optional[float] = Field(default=None, description="Latitude of the property centroid")
    longitude: Optional[float] = Field(default=None, description="Longitude of the property centroid")
    wealth_percentile: Optional[int] = Field(default=None, ge=0, le=100, description="ZIP code wealth percentile")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence score for solar detection")
    solar_present: Optional[bool] = Field(default=None, description="True if panels detected, False if absent, None if uncertain")


class LeadsResponse(BaseModel):
    leads: List[Lead]
    count: int = Field(..., ge=0)
