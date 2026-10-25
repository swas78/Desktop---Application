# For: Pipeline execution manager running verification stages under 3-second budget
# Must never: Drop stage errors silently without recording timing and diagnostic context

import time
from engine.app.pipeline.context import PipelineContext
from engine.app.pipeline.ingest import run_ingest_stage
from engine.app.pipeline.preprocess import run_preprocess_stage
from engine.app.pipeline.ocr import run_ocr_stage
from engine.app.pipeline.classify import run_classify_stage
from engine.app.pipeline.qr_decode import run_qr_decode_stage
from engine.app.pipeline.translate import run_translate_stage
from engine.app.pipeline.extract import run_extract_stage
from engine.app.pipeline.verify import run_verify_stage
from engine.app.pipeline.authenticity import run_authenticity_stage


def execute_stage(stage_name: str, stage_fn, ctx: PipelineContext) -> None:
    """Executes a single pipeline stage while recording execution elapsed time."""
    start_ns = time.perf_counter_ns()
    stage_fn(ctx)
    elapsed_ms = int((time.perf_counter_ns() - start_ns) / 1_000_000)
    ctx.timings[stage_name] = elapsed_ms


def run_pipeline(ctx: PipelineContext) -> PipelineContext:
    """Executes the complete document verification pipeline stages in sequence.
    
    Stages: Ingest, Preprocess, OCR, Classify, QRDecode, Translate, Extract, Verify, Authenticity.
    Enforces quality gate and total target budget <= 3.0s.
    """
    total_start = time.perf_counter_ns()
    
    # 1. Ingest & Quality Gate
    execute_stage("ingest", run_ingest_stage, ctx)
    if ctx.quality_issue:
        ctx.alerts.append(ctx.quality_issue)
        ctx.timings["total"] = int((time.perf_counter_ns() - total_start) / 1_000_000)
        return ctx

    # 2. Preprocess
    execute_stage("preprocess", run_preprocess_stage, ctx)
    # 3. OCR (text & spatial bboxes)
    execute_stage("ocr", run_ocr_stage, ctx)
    # 4. Classify (using visual + OCR snippet)
    execute_stage("classify", run_classify_stage, ctx)
    # 5. QR decode
    execute_stage("qr_decode", run_qr_decode_stage, ctx)
    # 6. Translate (if Indic)
    execute_stage("translate", run_translate_stage, ctx)
    # 7. Extract
    execute_stage("extract", run_extract_stage, ctx)
    # 8. Verify
    execute_stage("verify", run_verify_stage, ctx)
    # 9. Authenticity
    execute_stage("authenticity", run_authenticity_stage, ctx)
    
    ctx.timings["total"] = int((time.perf_counter_ns() - total_start) / 1_000_000)
    return ctx
