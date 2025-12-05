from typing import Any, Dict, Optional
import logging
import json

import httpx
try:
    import google.generativeai as genai
except ImportError:
    genai = None
from PIL import Image
import io

from ..config import get_settings


logger = logging.getLogger(__name__)


class GeminiVisionService:
    """Google Gemini Vision client wrapper for backyard analysis using image URLs."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._genai_available = genai is not None

        if not self._genai_available:
            logger.error("google-generativeai package not installed. Vision service will not work.")
            self._available_models = []
            return

        if not self.settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY not configured; GeminiVisionService will no-op")
            self._available_models = []
        else:
            genai.configure(api_key=self.settings.gemini_api_key)
            # Try to get available models on initialization
            try:
                available_models = [m.name.split('/')[-1] for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                logger.info(f"Available Gemini models: {available_models}")
                self._available_models = available_models
            except Exception as e:
                logger.warning(f"Could not list available models: {e}. Using default models.")
                # Fallback to known working models
                self._available_models = ["gemini-pro", "gemini-pro-vision"]
        self._http = httpx.Client(timeout=self.settings.vision_timeout_seconds)
        # Simple in-memory cache to avoid duplicate Gemini calls per image URL.
        # Cache format: { image_url: (timestamp_seconds, parsed_response_dict) }
        self._cache: dict[str, tuple[float, Dict[str, Any]]] = {}
        self._cache_ttl = getattr(self.settings, "vision_cache_ttl_seconds", 3600)

    def close(self) -> None:
        try:
            self._http.close()
        except Exception:
            logger.debug("Failed to close http client", exc_info=True)

    def classify(self, *, image_url: str, model: Optional[str] = None, confidence_threshold: Optional[float] = None, longitude: Optional[float] = None, latitude: Optional[float] = None) -> Dict[str, Any]:
        # Get model from parameter or settings, but ensure it's a Gemini model
        requested_model = model or self.settings.vision_model
        
        # Get available models (fallback to known working models)
        available_models = getattr(self, '_available_models', ["gemini-pro", "gemini-pro-vision"])
        
        # Prefer stable models over previews (filter out preview/experimental models)
        stable_models = [m for m in available_models if 'preview' not in m.lower() and 'exp' not in m.lower() and 'experimental' not in m.lower()]
        
        # Priority order for vision-capable models (most stable first)
        preferred_models = [
            "gemini-2.5-flash",      # Latest stable flash model
            "gemini-2.5-pro",        # Latest stable pro model
            "gemini-2.0-flash",      # Stable 2.0 flash
            "gemini-pro-vision",     # Legacy vision model
            "gemini-pro",            # Legacy pro model
        ]
        
        # Map OpenAI models to Gemini equivalents, or use best available model
        if requested_model.startswith("gpt-") or requested_model not in available_models:
            # Try preferred models in order
            for preferred in preferred_models:
                if preferred in available_models:
                    use_model = preferred
                    logger.info(f"Model '{requested_model}' not available. Using preferred stable model '{use_model}' instead.")
                    break
            else:
                # If no preferred model available, use first stable model, or first available
                if stable_models:
                    use_model = stable_models[0]
                    logger.warning(f"Using stable model '{use_model}' (not in preferred list)")
                else:
                    use_model = available_models[0] if available_models else "gemini-pro"
                    logger.warning(f"Using available model '{use_model}' (may be preview/experimental)")
        else:
            use_model = requested_model
            
        threshold = confidence_threshold if confidence_threshold is not None else self.settings.vision_confidence_threshold
        
        logger.info(f"Using vision model: {use_model}, Gemini API key configured: {bool(self.settings.gemini_api_key)}")
        
        if not self._genai_available:
            logger.error("google-generativeai package not available. Cannot perform vision analysis.")
            return {"backyard_status": "uncertain", "backyard_confidence": 0.0, "notes": "google-generativeai package not installed", "model": use_model}

        if not self.settings.gemini_api_key:
            logger.error("GEMINI_API_KEY not configured! Please add GEMINI_API_KEY to your .env file.")
            return {"backyard_status": "uncertain", "backyard_confidence": 0.0, "notes": "GEMINI_API_KEY not configured", "model": use_model}

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

        # Download image from URL
        try:
            img_resp = self._http.get(image_url)
            img_resp.raise_for_status()
            img_data = img_resp.content
            img = Image.open(io.BytesIO(img_data))
        except Exception as e:
            logger.error("Failed to download image from %s: %s", image_url, e)
            return {"backyard_status": "uncertain", "backyard_confidence": 0.0, "notes": f"Failed to load image: {str(e)}", "model": use_model}

        # Prepare prompt for Gemini
        prompt = f"""You are a backyard development analyst. Analyze this top-down satellite image (~512×512 px, zoom≈20) centered on a residential property and determine the development status of the backyard area.

Ignore any pins, map markers, overlays, or cartographic artifacts. Focus on the outdoor space behind the main building structure.

Visual cues for backyard classification:
- "undeveloped": Large areas of bare dirt, sparse grass, minimal or no landscaping, no pools, patios, decks, or hardscape features.
- "partially_developed": Some landscaping (trees, shrubs, grass) but significant undeveloped space, or basic features like a simple deck without full landscaping.
- "fully_landscaped": Mature landscaping, pools, patios, decks, extensive hardscape, well-maintained gardens, or clearly developed outdoor living spaces.
- "uncertain": Image quality too poor, backyard not visible, or ambiguous development status.

Do NOT confuse:
- Front yards with backyards (focus on the area behind the main structure).
- Temporary features (construction, vehicles) with permanent development.
- Small decorative elements with significant development.

Context:
- Source: Google Maps Static Satellite Image
- Location: (lon, lat) = {longitude}, {latitude}
- Decision threshold (THRESHOLD): {threshold}

Return ONLY a valid JSON object with this exact structure (no markdown, no code blocks, just the JSON):
{{
  "backyard_status": "undeveloped" | "partially_developed" | "fully_landscaped" | "uncertain",
  "confidence": 0.0-1.0,
  "notes": "Brief explanation"
}}

If your confidence is below {threshold}, return "backyard_status": "uncertain".
"""

        try:
            # Use Gemini model for vision analysis
            gemini_model = genai.GenerativeModel(use_model)
            response = gemini_model.generate_content(
                [prompt, img],
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                    response_mime_type="application/json",
                )
            )
            content = response.text.strip()
            logger.debug("Gemini response: %s", content)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API error with model '{use_model}': {error_msg}")
            
            # If model not found, try fallback models
            if "404" in error_msg and "not found" in error_msg.lower():
                fallback_models = ["gemini-pro", "gemini-pro-vision"]
                for fallback in fallback_models:
                    if fallback != use_model:
                        try:
                            logger.info(f"Trying fallback model: {fallback}")
                            gemini_model = genai.GenerativeModel(fallback)
                            response = gemini_model.generate_content(
                                [prompt, img],
                                generation_config=genai.types.GenerationConfig(
                                    temperature=0,
                                    response_mime_type="application/json",
                                )
                            )
                            content = response.text.strip()
                            use_model = fallback  # Update model name in response
                            logger.info(f"Successfully used fallback model: {fallback}")
                            break
                        except Exception as fallback_error:
                            logger.warning(f"Fallback model {fallback} also failed: {fallback_error}")
                            continue
                else:
                    # All models failed
                    return {"backyard_status": "uncertain", "backyard_confidence": 0.0, "notes": f"API error: {error_msg}", "model": use_model}
            else:
                return {"backyard_status": "uncertain", "backyard_confidence": 0.0, "notes": f"API error: {error_msg}", "model": use_model}

        # Parse JSON response from Gemini
        try:
            parsed = json.loads(content) if content else {}
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse Gemini JSON content: %s. Content: %s", e, content)
            # Try to extract JSON from markdown code blocks if present
            try:
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                    parsed = json.loads(content)
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                    parsed = json.loads(content)
                else:
                    parsed = {}
            except Exception:
                parsed = {}
        except Exception as e:
            logger.warning("Unexpected error parsing JSON: %s. Content: %s", e, content)
            parsed = {}

        # Cache the parsed result if enabled
        try:
            if getattr(self.settings, "vision_cache_enabled", True) and image_url:
                import time

                self._cache[image_url] = (time.time(), parsed)
        except Exception:
            logger.debug("Failed to write to vision cache", exc_info=True)

        # Map schema to our internal shape
        backyard_status = parsed.get("backyard_status") if isinstance(parsed, dict) else None
        confidence = parsed.get("confidence") if isinstance(parsed, dict) else None
        notes = parsed.get("notes") if isinstance(parsed, dict) else None

        # Validate backyard_status is one of the expected values
        valid_statuses = ("undeveloped", "partially_developed", "fully_landscaped", "uncertain")
        if backyard_status not in valid_statuses:
            backyard_status = "uncertain"
        
        # If confidence is below threshold, mark as uncertain
        if confidence is not None and isinstance(confidence, (float, int)) and confidence < threshold:
            backyard_status = "uncertain"

        result = {
            "backyard_status": backyard_status,
            "backyard_confidence": confidence,
            "notes": notes,
            "model": use_model,
        }
        logger.info(f"Vision classification result: backyard_status={backyard_status}, confidence={confidence}, model={use_model}")
        return result
