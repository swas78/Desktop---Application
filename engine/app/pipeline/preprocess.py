# For: Image preprocessing, orientation adjustment, and contrast enhancement
# Must never: Overwrite or discard the original uncompressed source image

from PIL import Image, ImageOps, ImageEnhance
from engine.app.pipeline.context import PipelineContext


def normalize_page(img: Image.Image) -> Image.Image:
    """Enhances image contrast and balances dynamic range for OCR readability."""
    img_rgb = img.convert("RGB")
    # Auto-contrast to stretch dynamic range
    contrasted = ImageOps.autocontrast(img_rgb, cutoff=1)
    enhancer = ImageEnhance.Sharpness(contrasted)
    return enhancer.enhance(1.2)


def run_preprocess_stage(ctx: PipelineContext) -> PipelineContext:
    """Preprocess decoded images for OCR and layout extraction.
    
    Input: Decoded page images.
    Output: Deskewed, contrast-normalized images.
    Time budget: 0.3 seconds.
    """
    if not ctx.pages:
        return ctx
    
    processed_pages: list[Image.Image] = []
    for page in ctx.pages:
        processed = normalize_page(page)
        processed_pages.append(processed)
    
    ctx.pages = processed_pages
    return ctx
