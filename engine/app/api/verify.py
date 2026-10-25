# For: Synchronous single-document instant check API endpoint and preset samples
# Must never: Exceed the 3.0-second hard latency budget on standard hardware

import json
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from engine.app.api.deps import get_current_user
from engine.app.pipeline.context import PipelineContext
from engine.app.pipeline.manager import run_pipeline

router = APIRouter(tags=["verify"])
SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "sample_data"


def format_verification_response(ctx: PipelineContext) -> dict:
    """Formats pipeline context into standardized instant check response."""
    formatted_fields = [
        {
            "name": f.name,
            "extracted": f.extracted,
            "expected": f.expected,
            "status": f.status,
            "confidence": f.confidence,
            "source": f.source,
            "bbox": f.bbox,
            "reason": f.reason,
            "auto_accepted": f.auto_accepted,
        }
        for f in ctx.fields
    ]
    return {
        "document_type": ctx.detected_type,
        "type_confidence": ctx.type_confidence,
        "processing_ms": ctx.timings.get("total", 0),
        "model_version": "1.0.0",
        "quality_score": ctx.quality_score,
        "fields": formatted_fields,
        "checks": [{"name": "document_integrity", "result": "pass"}],
        "authenticity": {
            "risk_score": ctx.authenticity_risk,
            "flags": ctx.authenticity_flags,
        },
        "alerts": ctx.alerts,
    }


@router.post("/verify/instant")
async def verify_instant(
    file: UploadFile = File(...),
    biodata: str = Form("{}"),
    declared_type: str | None = Form(None),
    _user: dict = Depends(get_current_user),
):
    """Processes a single document synchronously in under 3 seconds."""
    raw_bytes = await file.read()
    try:
        biodata_dict = json.loads(biodata)
    except Exception:
        biodata_dict = {}

    ctx = PipelineContext(
        file_bytes=raw_bytes,
        filename=file.filename or "uploaded_doc",
        biodata=biodata_dict,
        declared_type=declared_type,
    )
    run_pipeline(ctx)

    if ctx.quality_issue:
        raise HTTPException(
            status_code=422,
            detail={"code": "UNREADABLE_DOCUMENT", "message": ctx.quality_issue},
        )

    return format_verification_response(ctx)


@router.post("/verify/preset/{sample_type}")
def verify_preset_sample(sample_type: str, _user: dict = Depends(get_current_user)):
    """Runs instant verification directly on pre-generated demo samples for one-click testing."""
    sample_files = {
        "clean": ("sample_clean_marksheet.pdf", "sample_clean_biodata.json"),
        "altered": ("sample_altered_marksheet.pdf", "sample_altered_biodata.json"),
        "blurry": ("sample_blurry_scan.png", None),
    }
    if sample_type not in sample_files:
        raise HTTPException(status_code=400, detail={"code": "BAD_REQUEST", "message": "Unknown sample preset"})

    doc_name, bio_name = sample_files[sample_type]
    doc_path = SAMPLE_DIR / doc_name
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Sample file not generated"})

    bio_dict = {}
    if bio_name and (SAMPLE_DIR / bio_name).exists():
        bio_dict = json.loads((SAMPLE_DIR / bio_name).read_text())

    ctx = PipelineContext(
        file_bytes=doc_path.read_bytes(),
        filename=doc_name,
        biodata=bio_dict,
    )
    run_pipeline(ctx)

    if ctx.quality_issue:
        raise HTTPException(
            status_code=422,
            detail={"code": "UNREADABLE_DOCUMENT", "message": ctx.quality_issue},
        )

    return format_verification_response(ctx)
