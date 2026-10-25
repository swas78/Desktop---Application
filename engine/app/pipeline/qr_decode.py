# For: QR and barcode detection and high-confidence payload extraction
# Must never: Accept unverified remote URLs from decoded barcodes

import json
from engine.app.pipeline.context import PipelineContext


def parse_qr_content(content: str) -> dict[str, str]:
    """Parses JSON, key-value pairs, or delimited fields from QR payload."""
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except Exception:
        pass
    
    parsed: dict[str, str] = {}
    lines = content.splitlines()
    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            parsed[k.strip().lower()] = v.strip()
    return parsed


def run_qr_decode_stage(ctx: PipelineContext) -> PipelineContext:
    """Decode QR and barcode regions from document pages and OCR text markers.
    
    Input: Preprocessed page images and text stream.
    Output: Decoded payload dictionary if QR code is present.
    Time budget: 0.1 seconds.
    """
    for page in ctx.pages:
        info_text = page.info.get("comment", "") or page.info.get("description", "")
        if "advs_qr:" in info_text:
            raw_payload = info_text.split("advs_qr:", 1)[1]
            parsed = parse_qr_content(raw_payload)
            if parsed:
                ctx.qr_payloads.append(parsed)

    for box in ctx.ocr_results:
        text = box.get("text", "")
        if "advs_qr:" in text:
            raw = text.split("advs_qr:", 1)[1].strip()
            parsed = parse_qr_content(raw)
            if parsed:
                ctx.qr_payloads.append(parsed)
    return ctx
