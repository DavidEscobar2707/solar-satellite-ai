from solar_ai_backend.services.vision_agent import VisionAgent


def test_analyze_roof_returns_expected_keys() -> None:
    agent = VisionAgent()
    result = agent.analyze_roof("https://example.com/image.png")
    assert "mask_url" in result
    assert "confidence" in result and 0.0 <= result["confidence"] <= 1.0
    assert "bbox" in result and isinstance(result["bbox"], list) and len(result["bbox"]) == 4
    assert "solar_present" in result and isinstance(result["solar_present"], bool)

