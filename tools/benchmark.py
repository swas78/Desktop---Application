# For: Latency benchmarking and p95 performance validation harness
# Must never: Alter benchmark inputs dynamically to artificially lower latency numbers

import json
import time
from pathlib import Path
from engine.app.pipeline.context import PipelineContext
from engine.app.pipeline.manager import run_pipeline
from tools.synthetic_data import create_clean_marksheet_pdf, SAMPLE_DIR


def run_benchmark(num_runs: int = 25) -> dict:
    """Executes verification pipeline across sample documents and records latency metrics."""
    test_pdf = SAMPLE_DIR / "benchmark_doc.pdf"
    biodata = create_clean_marksheet_pdf(test_pdf)
    file_bytes = test_pdf.read_bytes()

    durations: list[float] = []
    stage_breakdown: dict[str, list[int]] = {}

    print(f"Starting performance benchmark ({num_runs} runs)...")
    for i in range(num_runs):
        ctx = PipelineContext(
            file_bytes=file_bytes,
            filename="benchmark_doc.pdf",
            biodata=biodata
        )
        start_ns = time.perf_counter_ns()
        run_pipeline(ctx)
        dur_sec = (time.perf_counter_ns() - start_ns) / 1_000_000_000.0
        durations.append(dur_sec)

        for stg, ms in ctx.timings.items():
            stage_breakdown.setdefault(stg, []).append(ms)

    durations.sort()
    p50 = durations[int(num_runs * 0.50)]
    p95 = durations[int(num_runs * 0.95)]
    avg = sum(durations) / len(durations)

    passed = p95 <= 3.0
    print("\n--- Benchmark Results ---")
    print(f"Runs: {num_runs}")
    print(f"Average time: {avg:.3f} s")
    print(f"p50 time:     {p50:.3f} s")
    print(f"p95 time:     {p95:.3f} s  (Target <= 3.0 s)")
    print(f"Quality Gate: {'PASSED' if passed else 'FAILED'}")
    return {"runs": num_runs, "avg": avg, "p50": p50, "p95": p95, "passed": passed}


if __name__ == "__main__":
    run_benchmark()
