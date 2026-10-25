# For: Document classification across RAC supported certificate and marksheet types
# Must never: Guess unsupported document categories without sending to manual review

from engine.app.pipeline.context import PipelineContext

DOC_TYPE_KEYWORDS = {
    "gate_scorecard": ["gate", "graduate aptitude test", "all india rank", "air", "gate score"],
    "degree_marksheet": ["bachelor", "degree", "b.tech", "b.e", "semester", "cgpa", "provisional"],
    "12th_marksheet": ["senior secondary", "higher secondary", "class xii", "intermediate", "12th"],
    "10th_marksheet": ["secondary school", "class x", "matriculation", "high school", "10th"],
    "caste_certificate": ["caste", "scheduled caste", "scheduled tribe", "obc", "other backward class", "tehsildar"],
    "ews_certificate": ["economically weaker sections", "ews", "gross annual income", "financial year"],
    "pwd_certificate": ["disability", "pwd", "locomotor", "visual impairment", "medical board"],
    "experience_letter": ["relieving", "experience certificate", "designation", "employment", "service"]
}


def score_text_against_keywords(text_lower: str, keywords: list[str]) -> int:
    """Counts matching keyword hits in the lowercased document text."""
    return sum(1 for kw in keywords if kw in text_lower)


def classify_document(raw_snippet: str, declared_type: str | None) -> tuple[str, float]:
    """Determines document type based on keyword frequency and declared hint."""
    text = raw_snippet.lower()
    best_type = "unknown"
    max_hits = 0
    
    for doc_type, keywords in DOC_TYPE_KEYWORDS.items():
        hits = score_text_against_keywords(text, keywords)
        if hits > max_hits:
            max_hits = hits
            best_type = doc_type
            
    if max_hits >= 2:
        confidence = min(0.99, 0.70 + (max_hits * 0.08))
        return best_type, round(confidence, 2)
    
    if declared_type and declared_type in DOC_TYPE_KEYWORDS:
        return declared_type, 0.85
    
    return "unknown", 0.40


def run_classify_stage(ctx: PipelineContext) -> PipelineContext:
    """Classify document into one of the RAC catalogue types.
    
    Input: Page images and text snippet.
    Output: Document type and confidence score.
    Time budget: 0.2 seconds.
    """
    sample_text = f"{ctx.filename} "
    if ctx.ocr_results:
        sample_text += " ".join(box.get("text", "") for box in ctx.ocr_results[:20])
    
    doc_type, confidence = classify_document(sample_text, ctx.declared_type)
    ctx.detected_type = doc_type
    ctx.type_confidence = confidence
    return ctx
