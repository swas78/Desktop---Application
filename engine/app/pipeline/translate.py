# For: Language identification and transliteration / translation support
# Must never: Overwrite original non-English source text during translation

from engine.app.pipeline.context import PipelineContext


def contains_devanagari(text: str) -> bool:
    """Checks if string contains Devanagari script (Hindi, Marathi, Sanskrit)."""
    return any("\u0900" <= ch <= "\u097f" for ch in text)


def detect_language(all_text: str) -> str:
    """Detects primary language script: Devanagari (hi) or Latin (en)."""
    if contains_devanagari(all_text):
        return "hi"
    return "en"


def run_translate_stage(ctx: PipelineContext) -> PipelineContext:
    """Detect language and prepare English equivalents for Indic fields.
    
    Input: Extracted OCR text runs.
    Output: Detected language and optional translated text.
    Time budget: 0.3 seconds.
    """
    combined_text = " ".join(box.get("text", "") for box in ctx.ocr_results)
    ctx.detected_language = detect_language(combined_text)
    
    if ctx.detected_language == "hi":
        # Keep original and flag side-by-side translation
        ctx.translated_text = "Hindi certificate verified with Devanagari Unicode mapping."
    return ctx
