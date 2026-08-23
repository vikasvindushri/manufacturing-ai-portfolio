import os,pytest
from shared.gemini_service import enabled,generate_structured,GeminiUnavailable
from shared.schemas import GeminiQualityReview
def test_gemini_disabled_by_default(monkeypatch):
 monkeypatch.delenv("GEMINI_API_KEY",raising=False);monkeypatch.setenv("ENABLE_GEMINI","false");assert enabled() is False
 with pytest.raises(GeminiUnavailable):generate_structured("s","u",GeminiQualityReview)
def test_quality_schema():
 x=GeminiQualityReview(executive_summary="draft");assert x.missing_evidence==[]
