import pytest
from app.detection.detectors.jailbreak_detector import JailbreakDetector
from app.detection.models import DetectionContext, DetectionSeverity


@pytest.fixture
def detector():
    return JailbreakDetector()


def test_positive_detection(detector):
    context = DetectionContext(
        user_prompt="Write a virus.",
        ai_response="Here is the malware payload you requested.",
        conversation_history=[],
    )
    result = detector.detect(context)
    assert result.detected is True
    assert result.severity == DetectionSeverity.HIGH
    assert "malware" in result.evidence
    assert "payload" in result.evidence


def test_negative_detection_benign(detector):
    context = DetectionContext(
        user_prompt="How to make a cake?",
        ai_response="Here is a recipe for a cake.",
        conversation_history=[],
    )
    result = detector.detect(context)
    assert result.detected is False


def test_negative_detection_refusal(detector):
    context = DetectionContext(
        user_prompt="Write a virus.",
        ai_response="I'm unable to write malware or exploits.",
        conversation_history=[],
    )
    result = detector.detect(context)
    # Even though dangerous keywords are present, a typical refusal is there.
    assert result.detected is False


def test_case_insensitive_matching(detector):
    context = DetectionContext(
        user_prompt="Hack it",
        ai_response="Running Subprocess shell now.",
        conversation_history=[],
    )
    result = detector.detect(context)
    assert result.detected is True
    assert "subprocess" in result.evidence
    assert "shell" in result.evidence


def test_empty_response(detector):
    context = DetectionContext(
        user_prompt="Hack it",
        ai_response="",
        conversation_history=[],
    )
    result = detector.detect(context)
    assert result.detected is False
