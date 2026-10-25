# For: Document-specific field extraction and bounding box association
# Must never: Invent extracted values that do not originate from document content

import re
from engine.app.pipeline.context import PipelineContext, ExtractedFieldData

FIELD_PATTERNS = {
    "full_name": [r"(?:name|candidate'?s name|shri|km)\s*[:\-]?\s*([A-Za-z\s\.]+)", r"(?:नाम)\s*[:\-]?\s*([^\n\r]+)"],
    "father_name": [r"(?:father'?s name|s/o|d/o|shri)\s*[:\-]?\s*([A-Za-z\s\.]+)", r"(?:पिता का नाम)\s*[:\-]?\s*([^\n\r]+)"],
    "dob": [r"(?:dob|date of birth|जन्म तिथि)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})"],
    "percentage": [r"(?:percentage|marks|aggregate)\s*[:\-]?\s*(\d{1,2}(?:\.\d{1,2})?)\s*%?"],
    "cgpa": [r"(?:cgpa|grade point)\s*[:\-]?\s*(\d{1,2}(?:\.\d{1,2})?)"],
    "roll_no": [r"(?:roll\s*(?:no|number)|enrolment|regn?\.?\s*no)\s*[:\-]?\s*([A-Za-z0-9\-\/]+)"],
    "gate_score": [r"(?:gate score|score)\s*[:\-]?\s*(\d{2,4})"],
    "all_india_rank": [r"(?:all india rank|air)\s*[:\-]?\s*(\d+)"],
    "category": [r"(?:category|caste|community)\s*[:\-]?\s*(UR|OBC|SC|ST|EWS)"],
    "financial_year": [r"(?:financial year|f\.?y\.?)\s*[:\-]?\s*(\d{4}[\-\/]\d{2,4})"],
    "disability_percentage": [r"(?:disability percentage|percentage of disability)\s*[:\-]?\s*(\d{1,2})%?"]
}


def find_field_in_text(field_name: str, text: str) -> tuple[str | None, float]:
    """Finds field value using regex patterns and returns value with confidence."""
    patterns = FIELD_PATTERNS.get(field_name, [])
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            return val, 0.95
    return None, 0.0


def extract_from_qr(qr_payload: dict[str, str]) -> list[ExtractedFieldData]:
    """Extracts typed fields from QR payload with high ground-truth confidence."""
    fields: list[ExtractedFieldData] = []
    for k, v in qr_payload.items():
        fields.append(ExtractedFieldData(
            name=k,
            extracted=v,
            normalized=v,
            confidence=0.99,
            source="qr",
            page_no=1,
            bbox={"page": 1, "x": 600, "y": 100, "w": 120, "h": 120}
        ))
    return fields


def extract_fields_from_ocr(ctx: PipelineContext) -> list[ExtractedFieldData]:
    """Extracts fields by scanning OCR text boxes and recording spatial coordinates."""
    extracted: list[ExtractedFieldData] = []
    full_text = "\n".join(b.get("text", "") for b in ctx.ocr_results)
    
    for field_name in FIELD_PATTERNS.keys():
        val, conf = find_field_in_text(field_name, full_text)
        if not val:
            continue
        
        # Match back to the specific OCR box for bounding box
        matched_box = next((b for b in ctx.ocr_results if val in b.get("text", "")), None)
        bbox = None
        if matched_box:
            bbox = {
                "page": matched_box.get("page", 1),
                "x": matched_box.get("x", 100),
                "y": matched_box.get("y", 100),
                "w": matched_box.get("w", 200),
                "h": matched_box.get("h", 25)
            }
        
        extracted.append(ExtractedFieldData(
            name=field_name,
            extracted=val,
            normalized=val,
            confidence=conf,
            source="ocr",
            page_no=bbox["page"] if bbox else 1,
            bbox=bbox
        ))
    return extracted


def run_extract_stage(ctx: PipelineContext) -> PipelineContext:
    """Extract catalogue fields from document OCR text runs and QR codes.
    
    Input: OCR boxes, page images, and QR payloads.
    Output: Typed fields with confidence and bounding boxes.
    Time budget: 0.5 seconds.
    """
    field_map: dict[str, ExtractedFieldData] = {}
    
    # 1. Start with OCR text extractions
    for f in extract_fields_from_ocr(ctx):
        field_map[f.name] = f
        
    # 2. QR code overrides with higher priority and 0.99 confidence
    for qr_dict in ctx.qr_payloads:
        for f in extract_from_qr(qr_dict):
            field_map[f.name] = f
            
    ctx.fields = list(field_map.values())
    return ctx
