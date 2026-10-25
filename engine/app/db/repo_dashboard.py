# For: Dashboard KPI metrics, ledger calculations, settings, and audit queries
# Must never: Return unaggregated personal applicant values in public dashboard payloads

import json
import sqlite3
from typing import Any


def get_dashboard_summary(conn: sqlite3.Connection) -> dict[str, Any]:
    """Computes high-level verification throughput, ledger breakdown, and time saved."""
    cursor = conn.execute("SELECT COUNT(*), COALESCE(AVG(total_ms), 0) FROM extraction_runs WHERE is_latest = 1;")
    row = cursor.fetchone()
    total_docs, avg_ms = row[0] or 0, round(row[1] or 0, 1)

    cur_p95 = conn.execute("SELECT total_ms FROM extraction_runs WHERE is_latest = 1 ORDER BY total_ms ASC;")
    all_times = [r[0] for r in cur_p95.fetchall()]
    p95_ms = all_times[int(len(all_times) * 0.95)] if all_times else 0

    cur_stat = conn.execute(
        """
        SELECT 
          COUNT(CASE WHEN status = 'verified' THEN 1 END),
          COUNT(CASE WHEN status = 'needs_review' THEN 1 END)
        FROM documents;
        """
    )
    stat_row = cur_stat.fetchone()
    auto_ver = stat_row[0] or 0
    in_review = stat_row[1] or 0
    auto_pct = round((auto_ver / total_docs * 100), 1) if total_docs > 0 else 0.0
    rev_pct = round((in_review / total_docs * 100), 1) if total_docs > 0 else 0.0

    cur_setting = conn.execute("SELECT value_json FROM settings WHERE key = 'manual_minutes_per_doc';")
    s_row = cur_setting.fetchone()
    manual_min = json.loads(s_row[0]) if s_row else 4
    hours_saved = round((auto_ver * manual_min) / 60.0, 1)

    ledger = get_dashboard_ledger(conn)
    return {
        "processed": total_docs,
        "avg_ms": avg_ms,
        "p95_ms": p95_ms,
        "auto_verified_percent": auto_pct,
        "review_percent": rev_pct,
        "hours_saved": hours_saved,
        "manual_minutes_per_doc": manual_min,
        "ledger": ledger
    }


def get_dashboard_ledger(conn: sqlite3.Connection) -> list[dict]:
    """Generates ledger breakdown grouped by document type."""
    cursor = conn.execute(
        """
        SELECT 
          COALESCE(d.detected_type, 'unclassified') as doc_type,
          COUNT(*) as processed,
          COUNT(CASE WHEN d.status = 'verified' THEN 1 END) as auto_verified,
          COUNT(CASE WHEN d.status = 'needs_review' THEN 1 END) as sent_to_review,
          COUNT(CASE WHEN d.status = 'mismatch' THEN 1 END) as mismatches,
          COALESCE(AVG(r.total_ms), 0) as avg_ms
        FROM documents d
        LEFT JOIN extraction_runs r ON d.id = r.document_id AND r.is_latest = 1
        GROUP BY doc_type
        ORDER BY processed DESC;
        """
    )
    rows = cursor.fetchall()
    return [
        {
            "document_type": r["doc_type"],
            "processed": r["processed"],
            "auto_verified": r["auto_verified"],
            "sent_to_review": r["sent_to_review"],
            "mismatches": r["mismatches"],
            "avg_ms": round(r["avg_ms"], 1)
        }
        for r in rows
    ]


def get_mismatches_summary(conn: sqlite3.Connection) -> list[dict]:
    """Aggregates mismatch counts by field name and reason."""
    cursor = conn.execute(
        """
        SELECT field_name, COALESCE(reason, 'Discrepancy detected') as reason, COUNT(*) as cnt
        FROM extracted_fields f
        JOIN extraction_runs r ON f.run_id = r.id AND r.is_latest = 1
        WHERE f.status = 'mismatch'
        GROUP BY field_name, reason
        ORDER BY cnt DESC LIMIT 20;
        """
    )
    return [{"field_name": r["field_name"], "reason": r["reason"], "count": r["cnt"]} for r in cursor.fetchall()]


def get_accuracy_metrics(conn: sqlite3.Connection) -> list[dict]:
    """Calculates field-level accuracy and review rate from human reviews."""
    cursor = conn.execute(
        """
        SELECT f.field_name, COALESCE(d.detected_type, 'generic') as doc_type,
               COUNT(*) as total_samples,
               1.0 - AVG(CASE WHEN rev.decision = 'corrected' THEN 1.0 ELSE 0.0 END) as accuracy,
               AVG(CASE WHEN f.auto_accepted = 0 THEN 1.0 ELSE 0.0 END) as review_rate
        FROM extracted_fields f
        JOIN documents d ON f.document_id = d.id
        LEFT JOIN field_reviews rev ON rev.field_id = f.id
        GROUP BY f.field_name, doc_type;
        """
    )
    rows = cursor.fetchall()
    return [
        {
            "field_name": r["field_name"],
            "document_type": r["doc_type"],
            "accuracy": round((r["accuracy"] or 1.0) * 100, 2),
            "sample_size": r["total_samples"],
            "review_rate": round((r["review_rate"] or 0.0) * 100, 1)
        }
        for r in rows
    ]
