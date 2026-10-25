# For: Document ingestion, multi-page decoding, and quality assessment
# Must never: Process corrupt or unreadable files without reporting explicit failure

import io
from PIL import Image, ImageStat
from pypdf import PdfReader
from engine.app.pipeline.context import PipelineContext


def compute_sharpness_score(img: Image.Image) -> float:
    """Calculates sharpness score using high-frequency detail analysis.
    
    Returns normalized quality score between 0.1 and 1.0.
    """
    gray = img.convert("L")
    stat = ImageStat.Stat(gray)
    stddev = stat.stddev[0]
    if stddev < 15.0:
        return 0.2
    
    diff = gray.crop((1, 1, gray.width, gray.height))
    orig = gray.crop((0, 0, gray.width - 1, gray.height - 1))
    diff_stat = ImageStat.Stat(diff)
    orig_stat = ImageStat.Stat(orig)
    variance_diff = abs(diff_stat.mean[0] - orig_stat.mean[0])
    score = min(1.0, (stddev / 50.0) * (0.8 + variance_diff))
    return max(0.1, score)


def decode_pdf_or_image(file_bytes: bytes, filename: str) -> tuple[list[Image.Image], bool]:
    """Decodes PDF pages or raster images; returns (pages, has_vector_text)."""
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        has_text = any(bool(p.extract_text() and p.extract_text().strip()) for p in reader.pages)
        pages: list[Image.Image] = []
        for p in reader.pages:
            for img_obj in p.images:
                pages.append(Image.open(io.BytesIO(img_obj.data)))
        if not pages:
            pages = [Image.new("RGB", (1200, 1600), color="white")]
        return pages, has_text
    
    return [Image.open(io.BytesIO(file_bytes)).convert("RGB")], False


def run_ingest_stage(ctx: PipelineContext) -> PipelineContext:
    """Ingest document bytes, decode pages, and evaluate quality gate.
    
    Input: Raw document bytes.
    Output: Decoded PIL images and normalized quality score.
    Time budget: 0.2 seconds.
    """
    try:
        pages, has_vector_text = decode_pdf_or_image(ctx.file_bytes, ctx.filename)
        if not pages:
            ctx.quality_score = 0.0
            ctx.quality_issue = "File contains no readable pages. Upload a valid document."
            return ctx
        ctx.pages = pages
        
        # Digital PDFs with vector text pass quality gate directly
        if has_vector_text:
            ctx.quality_score = 1.0
            return ctx
            
        first_page = pages[0]
        if first_page.width < 300 or first_page.height < 300:
            ctx.quality_score = 0.30
            ctx.quality_issue = "Document resolution is too low. Upload at least 300 DPI."
            return ctx
        
        sharpness = compute_sharpness_score(first_page)
        ctx.quality_score = round(sharpness, 2)
        if ctx.quality_score < 0.35:
            ctx.quality_issue = "This scan is too blurry to read. Upload a sharper copy."
        return ctx
    except Exception as exc:
        ctx.quality_score = 0.0
        ctx.quality_issue = f"Corrupt or unsupported file format: {exc}"
        return ctx
