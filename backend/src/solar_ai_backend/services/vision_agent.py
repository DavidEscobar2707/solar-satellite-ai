from typing import Any, Dict, Optional
import logging

import httpx

from ..config import get_settings


logger = logging.getLogger(__name__)


class OpenAIVisionService:
    """OpenAI Vision client wrapper for panel detection using image URLs."""

    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            logger.warning("OPENAI_API_KEY not configured; OpenAIVisionService will no-op")
        self._http = httpx.Client(timeout=self.settings.vision_timeout_seconds)
        # Simple in-memory cache to avoid duplicate OpenAI calls per image URL.
        # Cache format: { image_url: (timestamp_seconds, parsed_response_dict) }
        self._cache: dict[str, tuple[float, Dict[str, Any]]] = {}
        self._cache_ttl = getattr(self.settings, "vision_cache_ttl_seconds", 3600)

    def close(self) -> None:
        try:
            self._http.close()
        except Exception:
            logger.debug("Failed to close http client", exc_info=True)

    def classify(self, *, image_url: str, model: Optional[str] = None, confidence_threshold: Optional[float] = None, longitude: Optional[float] = None, latitude: Optional[float] = None) -> Dict[str, Any]:
        if not self.settings.openai_api_key:
            return {"solar_present": None, "confidence": None, "model": model or self.settings.vision_model}

        use_model = model or self.settings.vision_model
        threshold = confidence_threshold if confidence_threshold is not None else self.settings.vision_confidence_threshold

        # Check cache first
        try:
            if getattr(self.settings, "vision_cache_enabled", True) and image_url:
                entry = self._cache.get(image_url)
                if entry:
                    ts, parsed = entry
                    import time

                    if (time.time() - ts) < self._cache_ttl:
                        logger.debug("Vision cache hit for %s", image_url)
                        # Return cached shape, fill model field
                        parsed_copy = dict(parsed)
                        parsed_copy.setdefault("model", use_model)
                        return parsed_copy
                    else:
                        # expired
                        try:
                            del self._cache[image_url]
                        except Exception:
                            pass
        except Exception:
            logger.debug("Error checking vision cache", exc_info=True)

        # OpenAI responses via standard REST; using images in content
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        system_prompt = (
            "You are an expert remote-sensing analyst. Classify rooftop PV solar panel presence in nadir (top‑down) Mapbox Static Images (~512×512 px, zoom≈19). The image is centered on the target roof. Ignore any pins/overlays, labels, or cartographic artifacts.\n\n"
            "Decision cues: PV modules are dark, rectangular arrays with regular grid/cell pattern and specular highlights; do not confuse skylights, vents/HVAC, dark shingles, cars, or pure shadows.\n\n"
            "Output: Respond with strict JSON only, using this minimal schema:\n"
            "  {\n"
            "    \"answer\": \"yes\" | \"no\" | \"unable\",\n"
            "    \"confidence\": number\n"
            "  }\n"
            "If your confidence is below THRESHOLD, return \"unable\". Do not include any text outside the JSON object."
        )
        user_prompt = (
            f"Task: Determine if rooftop PV solar panels are present on the central property in this Mapbox tile. Ignore any map pins/markers; they may sit at the exact center.\n\n"
            f"Context:\n"
            f"- Source: Mapbox Static Images (satellite-v9), ~512×512 px, zoom: 19\n"
            f"- Location hint (lon,lat): {longitude},{latitude}\n"
            f"- Decision threshold (THRESHOLD): {threshold}\n\n"
            f"Image:\n"
            f"- URL: {image_url}\n\n"
            f"Return JSON only per the specified schema."
        )
        # Build a multimodal chat payload: pass text + image_url so the model
        # actually sees pixels. Ask for JSON-only response.
        payload = {
            "model": use_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }

        try:
            resp = self._http.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            # log full response for debugging when needed
            logger.debug("OpenAI response: %s", data)
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
        except httpx.HTTPError as exc:
            logger.warning("OpenAI Vision HTTP error: %s", exc)
            return {"solar_present": None, "confidence": None, "model": use_model}
        except Exception:
            logger.exception("OpenAI Vision unexpected error")
            return {"solar_present": None, "confidence": None, "model": use_model}

        # The assistant should return a JSON blob string per instructions.
        try:
            import json

            parsed = json.loads(content) if content else {}
        except Exception:
            logger.warning("Failed to parse assistant JSON content; returning raw content. Content: %s", content)
            parsed = {}

        # Cache the parsed result if enabled
        try:
            if getattr(self.settings, "vision_cache_enabled", True) and image_url:
                import time

                self._cache[image_url] = (time.time(), parsed)
        except Exception:
            logger.debug("Failed to write to vision cache", exc_info=True)

        # Map minimal schema to our internal shape
        answer = (parsed.get("answer") or "").strip().lower() if isinstance(parsed, dict) else ""
        confidence = parsed.get("confidence") if isinstance(parsed, dict) else None

        if answer in ("yes", "no", "unable"):
            if confidence is not None and isinstance(confidence, (float, int)) and confidence < threshold:
                solar_present = None
            else:
                solar_present = True if answer == "yes" else False if answer == "no" else None
        else:
            # Fallback for older schema
            solar_present = parsed.get("solar_present")
            if confidence is not None and isinstance(confidence, (float, int)) and confidence < threshold:
                solar_present = None

        return {
            "solar_present": solar_present,
            "confidence": confidence,
            "model": use_model,
        }
