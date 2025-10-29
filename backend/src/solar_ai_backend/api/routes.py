from typing import List, Dict, Any

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..config import get_settings
from ..schemas.models import (
    LocationRequest,
    LocationResponse,
    ImageMetadata,
    LeadGenerationRequest,
    LeadGenerationResponse,
    RoofAnalysis,
    LeadsEndpointRequest,
    LeadsEndpointResponse,
    LeadItem,
    Coordinates,
    ZillowMeta,
    ImageryMeta,
    VisionMeta,
)
from ..services.google_maps_client import GoogleMapsClient
from ..services.vision_agent import OpenAIVisionService
from ..services.enrichment import ZillowClient, LeadScorer
from ..utils.excel_export import leads_to_excel_b64, leads_to_excel_bytes, leads_to_csv_bytes, leads_to_csv_b64


logger = logging.getLogger(__name__)
router = APIRouter()


def _get_maps_client() -> GoogleMapsClient:
    settings = get_settings()
    if not settings.google_maps_api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_MAPS_API_KEY not configured")
    return GoogleMapsClient(api_key=settings.google_maps_api_key)


def _get_zillow_client() -> ZillowClient:
    settings = get_settings()
    if not settings.zillow_api_key:
        raise HTTPException(status_code=500, detail="ZILLOW_API_KEY not configured")
    return ZillowClient(
        api_key=settings.zillow_api_key,
        base_url=settings.zillow_api_base,
        rapidapi_host=settings.zillow_rapidapi_host,
    )


def _get_vision_service() -> OpenAIVisionService:
    return OpenAIVisionService()


@router.post("/validate-location", response_model=LocationResponse)
def validate_location(payload: LocationRequest) -> LocationResponse:
    try:
        client = _get_maps_client()
        lon, lat = client.validate_location(payload.location)
    except ValueError as ve:
        logger.info("Validation failed for location '%s': %s", payload.location, ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:  # pragma: no cover - generic guard
        logger.exception("Unexpected error during location validation")
        raise HTTPException(status_code=502, detail="Failed to validate location") from exc

    # Generate a few preview images for UI consumption
    try:
        urls: List[str] = client.get_satellite_images((lon, lat), count=3)
    except Exception:  # pragma: no cover
        logger.warning("Failed to obtain preview images", exc_info=True)
        urls = []
    finally:
        client.close()

    previews = [
        ImageMetadata(
            url=u,
            width=get_settings().mapbox_image_size,
            height=get_settings().mapbox_image_size,
            zoom=get_settings().mapbox_zoom,
            center_longitude=lon,
            center_latitude=lat,
            style=get_settings().mapbox_style,
        )
        for u in urls
        if u
    ]

    # We default to US here; schemas will enforce
    return LocationResponse(
        longitude=lon,
        latitude=lat,
        place_name=None,
        country_code=get_settings().mapbox_country_filter,
        confidence=1.0,
        bbox=None,
        previews=previews,
    )


@router.post("/generate-lead", response_model=LeadGenerationResponse)
def generate_lead(payload: LeadGenerationRequest) -> LeadGenerationResponse:
    client = _get_maps_client()
    try:
        lon, lat = client.validate_location(payload.location)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:  # pragma: no cover
        logger.exception("Location validation failed")
        raise HTTPException(status_code=502, detail="Failed to validate location") from exc

    # Fetch candidate satellite images
    try:
        image_urls = client.get_satellite_images((lon, lat), count=payload.limit)
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed fetching satellite images")
        raise HTTPException(status_code=502, detail="Failed to fetch satellite images") from exc
    finally:
        client.close()

    # Analyze each image with OpenAI Vision (replaces legacy VisionAgent)
    vision = _get_vision_service()
    analyses: list[RoofAnalysis] = []
    for url in image_urls:
        result = vision.classify(image_url=url)
        analyses.append(
            RoofAnalysis(
                image_url=url,
                bbox=None,
                confidence=result.get("confidence"),
                mask_url=None,
                solar_present=result.get("solar_present"),
                polygons=[],
                mask_rle=None,
            )
        )
    vision.close()

    return LeadGenerationResponse(
        longitude=lon,
        latitude=lat,
        analyses=analyses,
        count=len(analyses),
        input={"location": payload.location, "limit": payload.limit},
        enrichment={},
    )


@router.post("/leads", response_model=LeadsEndpointResponse)
def create_leads(payload: LeadsEndpointRequest) -> LeadsEndpointResponse:
    settings = get_settings()
    # Defaults from settings if not provided
    max_props = payload.max_properties or settings.leads_max_properties
    vision_model = payload.vision.model if payload.vision and payload.vision.model else settings.vision_model
    confidence_threshold = (
        payload.vision.confidence_threshold if payload.vision and payload.vision.confidence_threshold is not None
        else settings.vision_confidence_threshold
    )
    zoom = payload.imagery.zoom if payload.imagery else settings.mapbox_zoom
    size_w = payload.imagery.size.w if payload.imagery else settings.mapbox_image_size
    size_h = payload.imagery.size.h if payload.imagery else settings.mapbox_image_size

    # Fetch leads in batches until we have enough
    target_leads = payload.max_properties or settings.leads_max_properties
    all_properties = []
    batch_size = 50  # Start with 50 and increase if needed
    max_attempts = 5  # Prevent infinite loops
    page = 1  # Start with page 1

    zillow = _get_zillow_client()
    while len(all_properties) < target_leads * 2 and page <= max_attempts:  # Fetch extra to account for filtering
        try:
            batch = zillow.search_properties(
                location=payload.location,
                max_properties=batch_size,
                filters=(payload.zillow_filters.model_dump() if payload.zillow_filters else None),
                page=page,
            )
            all_properties.extend(batch)
            logger.info(f"Fetched {len(batch)} properties from page {page}, total so far: {len(all_properties)}")
            page += 1

            # If we got fewer results than requested, we've likely reached the end
            if len(batch) < batch_size:
                logger.info(f"Reached end of results at page {page-1}")
                break
        except ValueError as ve:
            logger.error(f"Zillow API error on page {page}: {ve}")
            break

    zillow.close()

    # Build imagery URLs per property and filter
    maps_client = _get_maps_client()
    leads: List[LeadItem] = []
    vision = _get_vision_service()
    scorer = LeadScorer()
    seen_results: dict[str, Dict[str, Any]] = {}
    try:
        for prop in all_properties:
            lat = prop.get("lat")
            lng = prop.get("lng")
            if lat is None or lng is None:
                continue
            img_url = maps_client.get_satellite_image_url(
                longitude=float(lng),
                latitude=float(lat),
                zoom=zoom,
                width_px=size_w,
                height_px=size_h,
            )

            # Reuse vision result if we've already processed the same image URL
            if img_url in seen_results:
                logger.debug("Reusing cached vision result for %s", img_url)
                vision_result = seen_results[img_url]
            else:
                vision_result = vision.classify(
                    image_url=img_url,
                    model=vision_model,
                    confidence_threshold=confidence_threshold,
                    longitude=float(lng),
                    latitude=float(lat),
                )
                seen_results[img_url] = vision_result

            if vision_result.get("solar_present") is True and vision_result.get("confidence", 0) > 0.8:
                # Skip only if AI is highly confident solar is present; include uncertain as leads
                continue

            score = scorer.score(price=prop.get("price"), living_area=prop.get("livingArea"))

            leads.append(
                LeadItem(
                    address=prop.get("address"),
                    coordinates=Coordinates(lat=float(lat), lng=float(lng)),
                    zillow=ZillowMeta(
                        zpid=str(prop.get("zpid")) if prop.get("zpid") is not None else None,
                        price=prop.get("price"),
                        beds=prop.get("beds"),
                        baths=prop.get("baths"),
                        livingArea=prop.get("livingArea"),
                    ),
                    imagery=ImageryMeta(
                        image_url=img_url,
                        zoom=zoom,
                        size={"w": size_w, "h": size_h},
                    ),
                    vision=VisionMeta(
                        solar_present=vision_result.get("solar_present"),
                        confidence=vision_result.get("confidence"),
                        model=vision_result.get("model"),
                        lead_score=vision_result.get("lead_score"),
                    ),
                    lead_score=score,
                )
            )

            # Early exit if we have enough leads
            if len(leads) >= target_leads:
                break
    finally:
        try:
            maps_client.close()
        except Exception:
            logger.debug("Mapbox client close failed", exc_info=True)
        try:
            vision.close()
        except Exception:
            logger.debug("Vision service close failed", exc_info=True)

    # Sort by lead_score desc and limit to target
    leads_sorted = sorted(leads, key=lambda x: x.lead_score, reverse=True)[:target_leads]

    # Convert Pydantic objects to dict for exporter
    leads_serializable = [l.model_dump() if hasattr(l, "model_dump") else l for l in leads_sorted]
    
    # CSV attachment (lightweight alternative to Excel)
    try:
        csv_payload = leads_to_csv_b64(leads_serializable, filename=f"leads-{payload.location.replace(' ', '_')}.csv")
    except Exception:
        logger.exception("Failed generating CSV payload")
        csv_payload = None
        # Fall back to Excel if CSV fails
        try:
            excel_payload = leads_to_excel_b64(leads_serializable, filename=f"leads-{payload.location.replace(' ', '_')}.xlsx")
        except Exception:
            logger.exception("Failed generating Excel payload")
            excel_payload = None
    else:
        # Only generate Excel if CSV succeeded (to avoid duplicate errors)
        excel_payload = None

    return LeadsEndpointResponse(
        location=payload.location,
        count=len(leads_sorted),
        leads=leads_sorted,
        excel=excel_payload,
        csv=csv_payload,  # New field for CSV
    )


@router.post("/leads/excel")
def create_leads_excel(payload: LeadsEndpointRequest) -> Response:
    """Return the leads as an XLSX binary download.

    Note: This mirrors the logic of /leads to build the same set of leads,
    but streams the Excel file rather than embedding base64.
    """
    # Build leads using the same orchestration as create_leads
    settings = get_settings()
    max_props = payload.max_properties or settings.leads_max_properties
    zoom = payload.imagery.zoom if payload.imagery else settings.mapbox_zoom
    size_w = payload.imagery.size.w if payload.imagery else settings.mapbox_image_size
    size_h = payload.imagery.size.h if payload.imagery else settings.mapbox_image_size
    vision_model = payload.vision.model if payload.vision and payload.vision.model else settings.vision_model
    confidence_threshold = (
        payload.vision.confidence_threshold if payload.vision and payload.vision.confidence_threshold is not None
        else settings.vision_confidence_threshold
    )

    zillow = _get_zillow_client()
    try:
        # Fetch properties with pagination for variety
        properties = []
        batch_size = 50
        max_pages = 5
        page = 1

        while len(properties) < max_props and page <= max_pages:
            batch = zillow.search_properties(
                location=payload.location,
                max_properties=batch_size,
                filters=(payload.zillow_filters.model_dump() if payload.zillow_filters else None),
                page=page,
            )
            properties.extend(batch)
            page += 1

            # If we got fewer results than requested, we've likely reached the end
            if len(batch) < batch_size:
                break

        # Limit to requested max_properties
        properties = properties[:max_props]
    finally:
        zillow.close()

    maps_client = _get_maps_client()
    vision = _get_vision_service()
    scorer = LeadScorer()
    leads: List[LeadItem] = []
    seen_results: dict[str, Dict[str, Any]] = {}
    try:
        for prop in properties:
            lat = prop.get("lat")
            lng = prop.get("lng")
            if lat is None or lng is None:
                continue
            img_url = maps_client.get_satellite_image_url(
                longitude=float(lng),
                latitude=float(lat),
                zoom=zoom,
                width_px=size_w,
                height_px=size_h,
            )
            if img_url in seen_results:
                vision_result = seen_results[img_url]
            else:
                vision_result = vision.classify(
                    image_url=img_url,
                    model=vision_model,
                    confidence_threshold=confidence_threshold,
                    longitude=float(lng),
                    latitude=float(lat),
                )
                seen_results[img_url] = vision_result
            if vision_result.get("solar_present") is True:
                continue
            score = scorer.score(price=prop.get("price"), living_area=prop.get("livingArea"))
            leads.append(
                LeadItem(
                    address=prop.get("address"),
                    coordinates=Coordinates(lat=float(lat), lng=float(lng)),
                    zillow=ZillowMeta(
                        zpid=str(prop.get("zpid")) if prop.get("zpid") is not None else None,
                        price=prop.get("price"),
                        beds=prop.get("beds"),
                        baths=prop.get("baths"),
                        livingArea=prop.get("livingArea"),
                    ),
                    imagery=ImageryMeta(
                        image_url=img_url,
                        zoom=zoom,
                        size={"w": size_w, "h": size_h},
                    ),
                    vision=VisionMeta(
                        solar_present=vision_result.get("solar_present"),
                        confidence=vision_result.get("confidence"),
                        model=vision_result.get("model"),
                        lead_score=vision_result.get("lead_score"),
                    ),
                    lead_score=score,
                )
            )
    finally:
        try:
            maps_client.close()
        except Exception:
            logger.debug("Mapbox client close failed", exc_info=True)
        try:
            vision.close()
        except Exception:
            logger.debug("Vision service close failed", exc_info=True)

    leads_sorted = sorted(leads, key=lambda x: x.lead_score, reverse=True)
    leads_serializable = [l.model_dump() if hasattr(l, "model_dump") else l for l in leads_sorted]
    data = leads_to_excel_bytes(leads_serializable)
    filename = f"leads-{payload.location.replace(' ', '_')}.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.post("/leads/csv")
def create_leads_csv(payload: LeadsEndpointRequest) -> Response:
    """Return the leads as a CSV binary download.

    Note: This is a lightweight alternative to Excel, providing the same data
    in a simpler format that's easier to process.
    """
    # Build leads using the same orchestration as create_leads
    settings = get_settings()
    max_props = payload.max_properties or settings.leads_max_properties
    zoom = payload.imagery.zoom if payload.imagery else settings.mapbox_zoom
    size_w = payload.imagery.size.w if payload.imagery else settings.mapbox_image_size
    size_h = payload.imagery.size.h if payload.imagery else settings.mapbox_image_size
    vision_model = payload.vision.model if payload.vision and payload.vision.model else settings.vision_model
    confidence_threshold = (
        payload.vision.confidence_threshold if payload.vision and payload.vision.confidence_threshold is not None
        else settings.vision_confidence_threshold
    )

    zillow = _get_zillow_client()
    try:
        # Fetch properties with pagination for variety
        properties = []
        batch_size = 50
        max_pages = 5
        page = 1

        while len(properties) < max_props and page <= max_pages:
            batch = zillow.search_properties(
                location=payload.location,
                max_properties=batch_size,
                filters=(payload.zillow_filters.model_dump() if payload.zillow_filters else None),
                page=page,
            )
            properties.extend(batch)
            page += 1

            # If we got fewer results than requested, we've likely reached the end
            if len(batch) < batch_size:
                break

        # Limit to requested max_properties
        properties = properties[:max_props]
    finally:
        zillow.close()

    maps_client = _get_maps_client()
    vision = _get_vision_service()
    scorer = LeadScorer()
    leads: List[LeadItem] = []
    seen_results: dict[str, Dict[str, Any]] = {}
    try:
        for prop in properties:
            lat = prop.get("lat")
            lng = prop.get("lng")
            if lat is None or lng is None:
                continue
            img_url = maps_client.get_satellite_image_url(
                longitude=float(lng),
                latitude=float(lat),
                zoom=zoom,
                width_px=size_w,
                height_px=size_h,
            )
            if img_url in seen_results:
                vision_result = seen_results[img_url]
            else:
                vision_result = vision.classify(
                    image_url=img_url,
                    model=vision_model,
                    confidence_threshold=confidence_threshold,
                    longitude=float(lng),
                    latitude=float(lat),
                )
                seen_results[img_url] = vision_result
            if vision_result.get("solar_present") is True:
                continue
            score = scorer.score(price=prop.get("price"), living_area=prop.get("livingArea"))
            leads.append(
                LeadItem(
                    address=prop.get("address"),
                    coordinates=Coordinates(lat=float(lat), lng=float(lng)),
                    zillow=ZillowMeta(
                        zpid=str(prop.get("zpid")) if prop.get("zpid") is not None else None,
                        price=prop.get("price"),
                        beds=prop.get("beds"),
                        baths=prop.get("baths"),
                        livingArea=prop.get("livingArea"),
                    ),
                    imagery=ImageryMeta(
                        image_url=img_url,
                        zoom=zoom,
                        size={"w": size_w, "h": size_h},
                    ),
                    vision=VisionMeta(
                        solar_present=vision_result.get("solar_present"),
                        confidence=vision_result.get("confidence"),
                        model=vision_result.get("model"),
                        lead_score=vision_result.get("lead_score"),
                    ),
                    lead_score=score,
                )
            )
    finally:
        try:
            maps_client.close()
        except Exception:
            logger.debug("Mapbox client close failed", exc_info=True)
        try:
            vision.close()
        except Exception:
            logger.debug("Vision service close failed", exc_info=True)

    leads_sorted = sorted(leads, key=lambda x: x.lead_score, reverse=True)
    leads_serializable = [l.model_dump() if hasattr(l, "model_dump") else l for l in leads_sorted]
    data = leads_to_csv_bytes(leads_serializable)
    filename = f"leads-{payload.location.replace(' ', '_')}.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(
        content=data,
        media_type="text/csv",
        headers=headers,
    )