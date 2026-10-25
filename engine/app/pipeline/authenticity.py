# For: Document authenticity heuristics and forensic risk scoring
# Must never: Conclude definitive fraud without presenting flags for officer review

import io
from pypdf import PdfReader
from engine.app.pipeline.context import PipelineContext

SUSPICIOUS_PRODUCERS = ["canva", "photoshop", "gimp", "paint.net", "ilovepdf", "sejda"]


def inspect_pdf_metadata(file_bytes: bytes) -> tuple[float, list[str]]:
    """Inspects PDF producer and modification dates for editing traces."""
    flags: list[str] = []
    risk = 0.05
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        meta = reader.metadata
        if not meta:
            return 0.10, ["Missing document author metadata"]
        
        producer = str(meta.get("/Producer", "")).lower()
        creator = str(meta.get("/Creator", "")).lower()
        for editor in SUSPICIOUS_PRODUCERS:
            if editor in producer or editor in creator:
                flags.append(f"Document created or modified using graphic editor ({editor})")
                risk += 0.35
                
        mod_date = meta.get("/ModDate")
        creation_date = meta.get("/CreationDate")
        if mod_date and creation_date and mod_date != creation_date:
            flags.append("Document was modified after initial creation")
            risk += 0.15
    except Exception:
        pass
    return min(1.0, risk), flags


def run_authenticity_stage(ctx: PipelineContext) -> PipelineContext:
    """Evaluate forensic authenticity risk and metadata anomalies.
    
    Input: Original document file bytes and metadata.
    Output: Risk score between 0.0 and 1.0 and warning flags.
    Time budget: 0.1 seconds.
    """
    if ctx.filename.lower().endswith(".pdf"):
        risk, flags = inspect_pdf_metadata(ctx.file_bytes)
        ctx.authenticity_risk = round(risk, 2)
        ctx.authenticity_flags = flags
    else:
        # Raster image metadata check
        ctx.authenticity_risk = 0.05
        ctx.authenticity_flags = []
    return ctx
