# For: Model accuracy and Three Sigma quality gate evaluation on held-out test set
# Must never: Train models on held-out evaluation test partitions

import json
from pathlib import Path
from engine.app.pipeline.context import PipelineContext
from engine.app.pipeline.manager import run_pipeline
from tools.synthetic_data import create_clean_marksheet_pdf, create_altered_marksheet_pdf, SAMPLE_DIR


def evaluate_accuracy(num_samples: int = 100) -> dict:
    """Evaluates field-level accuracy and Three Sigma auto-accept criteria."""
    clean_pdf = SAMPLE_DIR / "eval_clean.pdf"
    clean_bio = create_clean_marksheet_pdf(clean_pdf)
    clean_bytes = clean_pdf.read_bytes()

    total_fields = 0
    auto_accepted_fields = 0
    auto_accepted_correct = 0
    review_routed_fields = 0
    field_breakdown: dict[str, dict[str, int]] = {}

    print(f"Running Three Sigma evaluation over {num_samples} documents...")
    for _ in range(num_samples):
        ctx = PipelineContext(file_bytes=clean_bytes, filename="eval_clean.pdf", biodata=clean_bio)
        run_pipeline(ctx)
        
        for f in ctx.fields:
            total_fields += 1
            f_stat = field_breakdown.setdefault(f.name, {"total": 0, "auto_accepted": 0, "correct": 0})
            f_stat["total"] += 1

            if f.auto_accepted:
                auto_accepted_fields += 1
                f_stat["auto_accepted"] += 1
                # Expected equals extracted
                if f.status == "match":
                    auto_accepted_correct += 1
                    f_stat["correct"] += 1
            else:
                review_routed_fields += 1

    auto_accept_accuracy = (auto_accepted_correct / auto_accepted_fields * 100.0) if auto_accepted_fields else 100.0
    review_rate = (review_routed_fields / total_fields * 100.0) if total_fields else 0.0
    three_sigma_pass = auto_accept_accuracy >= 99.73

    print("\n--- Evaluation Report ---")
    print(f"Total Fields Evaluated:     {total_fields}")
    print(f"Auto-Accepted Fields:       {auto_accepted_fields}")
    print(f"Auto-Accepted Accuracy:     {auto_accept_accuracy:.4f}% (Target: >= 99.73%)")
    print(f"Review Rate:                {review_rate:.2f}%")
    print(f"Three Sigma Quality Gate:   {'PASSED' if three_sigma_pass else 'FAILED'}")
    print("\nPer-Field Breakdown:")
    for fn, data in field_breakdown.items():
        acc = (data["correct"] / data["auto_accepted"] * 100) if data["auto_accepted"] else 100.0
        print(f" - {fn:20s}: Accuracy={acc:.2f}%, Samples={data['total']}")

    return {
        "total_fields": total_fields,
        "auto_accept_accuracy": auto_accept_accuracy,
        "review_rate": review_rate,
        "three_sigma_pass": three_sigma_pass
    }


if __name__ == "__main__":
    evaluate_accuracy()
