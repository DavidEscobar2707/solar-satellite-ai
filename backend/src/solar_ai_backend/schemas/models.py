from typing import Optional, List, Dict, Any, Tuple

from pydantic import BaseModel, Field, field_validator


class LeadsRequest(BaseModel):
    """Deprecated in favor of LeadsEndpointRequest."""
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


class LocationRequest(BaseModel):
    location: str = Field(..., min_length=2, description="Free-form US location text")


class ImageMetadata(BaseModel):
    url: str
    width: int
    height: int
    zoom: int
    center_longitude: float
    center_latitude: float
    style: Optional[str] = None


class LocationResponse(BaseModel):
    longitude: float
    latitude: float
    place_name: Optional[str] = None
    country_code: str = Field("US", description="ISO 3166-1 alpha-2 country code")
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    bbox: Optional[List[float]] = None
    previews: List[ImageMetadata] = Field(default_factory=list)

    @field_validator("country_code")
    @classmethod
    def _country_must_be_us(cls, v: str) -> str:
        if v.upper() != "US":
            raise ValueError("Only US locations are supported")
        return v


class RoofAnalysis(BaseModel):
    image_url: str
    bbox: Optional[List[int]] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    mask_url: Optional[str] = None
    solar_present: Optional[bool] = None
    polygons: Optional[List[List[Tuple[float, float]]]] = None
    mask_rle: Optional[str] = None


class LeadGenerationRequest(BaseModel):
    location: str = Field(..., description="User-provided location text")
    limit: int = Field(default=6, ge=1, le=50, description="Number of images to analyze")


class LeadGenerationResponse(BaseModel):
    longitude: float
    latitude: float
    analyses: List[RoofAnalysis]
    count: int
    input: Dict[str, Any] = Field(default_factory=dict)
    enrichment: Dict[str, Any] = Field(default_factory=dict)


# ======================
# New `/api/v1/leads` models
# ======================


class ZillowFilters(BaseModel):
    minBeds: Optional[int] = Field(default=None, ge=0)
    minBaths: Optional[int] = Field(default=None, ge=0)
    propertyType: Optional[List[str]] = None
    minPrice: Optional[int] = Field(default=None, ge=0)
    maxPrice: Optional[int] = Field(default=None, ge=0)
    statusType: Optional[str] = Field(default=None)  # e.g., "RecentlySold", "ForSale"
    isNewConstruction: Optional[bool] = Field(default=None)
    isAuction: Optional[bool] = Field(default=None)
    preForeclosure: Optional[bool] = Field(default=None)
    saleByOwner: Optional[str] = Field(default=None)  # e.g., "true"
    maxMonthlyCostPayment: Optional[int] = Field(default=None, ge=0)
    sqft: Optional[int] = Field(default=None, ge=0)
    small: Optional[bool] = Field(default=None)
    large: Optional[bool] = Field(default=None)


class ImageSize(BaseModel):
    w: int = Field(default=512, ge=64, le=2048)
    h: int = Field(default=512, ge=64, le=2048)


class ImageryParams(BaseModel):
    zoom: int = Field(default=20, ge=20, le=20)
    size: ImageSize = Field(default_factory=ImageSize)


class VisionParams(BaseModel):
    model: str = Field(default="gpt-4o-mini")
    confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)


class LeadsEndpointRequest(BaseModel):
    location: str = Field(..., min_length=2)
    max_properties: int = Field(default=20, ge=1, le=200)
    zillow_filters: Optional[ZillowFilters] = None
    imagery: Optional[ImageryParams] = None
    vision: Optional[VisionParams] = None


class Coordinates(BaseModel):
    lat: float
    lng: float


class ZillowMeta(BaseModel):
    zpid: Optional[str] = None
    price: Optional[float] = None
    beds: Optional[int] = None
    baths: Optional[float] = None
    livingArea: Optional[int] = None


class ImageryMeta(BaseModel):
    image_url: str
    zoom: int
    size: ImageSize


class VisionMeta(BaseModel):
    solar_present: Optional[bool] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    model: Optional[str] = None


class LeadItem(BaseModel):
    address: Optional[str] = None
    coordinates: Coordinates
    zillow: ZillowMeta
    imagery: ImageryMeta
    vision: VisionMeta
    lead_score: float = Field(ge=0.0, le=1.0)


class LeadsEndpointResponse(BaseModel):
    location: str
    count: int = Field(..., ge=0)
    leads: List[LeadItem]
    excel: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional Excel attachment with keys: filename, base64",
    )
    csv: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional CSV attachment with keys: filename, base64",
    )
