# For: Pipeline context object carrying document state across stages
# Must never: Persist unencrypted applicant data to disk directly

from dataclasses import dataclass, field
from typing import Any
from PIL import Image


@dataclass
class BBox:
    page: int
    x: int
    y: int
    w: int
    h: number = 0


@dataclass
class ExtractedFieldData:
    name: str
    extracted: str | None
    normalized: str | None = None
    expected: str | None = None
    status: str = "low_confidence"
    confidence: float = 0.0
    source: str = "ocr"
    page_no: int = 1
    bbox: dict[str, int] | None = None
    reason: str | None = None
    auto_accepted: bool = False


@dataclass
class PipelineContext:
    file_bytes: bytes
    filename: str
    biodata: dict[str, Any] = field(default_factory=dict)
    declared_type: str | None = None
    mode: str = "quick"
    
    # Stage Outputs
    pages: list[Image.Image] = field(default_factory=list)
    quality_score: float = 1.0
    quality_issue: str | None = None
    detected_type: str = "unknown"
    type_confidence: float = 0.0
    qr_payloads: list[dict[str, Any]] = field(default_factory=list)
    ocr_results: list[dict[str, Any]] = field(default_factory=list)
    detected_language: str = "en"
    translated_text: str | None = None
    fields: list[ExtractedFieldData] = field(default_factory=list)
    checks: list[dict[str, Any]] = field(default_factory=list)
    authenticity_risk: float = 0.0
    authenticity_flags: list[str] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)
    timings: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
