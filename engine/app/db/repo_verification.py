# For: Extraction runs, extracted field persistence, and reviewer workbench queue
# Must never: Alter verified field ground truths without recording the reviewer identity

import json
import sqlite3
import uuid
from datetime import datetime, timezone


def save_extraction_run(conn: sqlite3.Connection, doc_id: str, mode: str, total_ms: int, timings: dict) -> str:
    """Creates a new extraction run and marks previous runs as not latest."""
    run_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("UPDATE extraction_runs SET is_latest = 0 WHERE document_id = ?;", (doc_id,))
    conn.execute(
        """
        INSERT INTO extraction_runs (id, document_id, mode, started_at, total_ms, timings_json, status, is_latest)
        VALUES (?, ?, ?, ?, ?, ?, 'completed', 1);
        """,
        (run_id, doc_id, mode, now, total_ms, json.dumps(timings))
    )
    return run_id


def save_extracted_fields(conn: sqlite3.Connection, run_id: str, doc_id: str, fields: list) -> None:
    """Inserts all extracted fields with coordinates and auto-accepted status."""
    for f in fields:
        field_id = str(uuid.uuid4())
        bbox_json = json.dumps(f.bbox) if f.bbox else None
        conn.execute(
            """
            INSERT INTO extracted_fields (id, run_id, document_id, field_name, extracted_value, normalized_value, expected_value, status, confidence, source, page_no, bbox_json, reason, auto_accepted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                field_id, run_id, doc_id, f.name, f.extracted, f.normalized, f.expected,
                f.status, f.confidence, f.source, f.page_no, bbox_json, f.reason,
                1 if f.auto_accepted else 0
            )
        )


def create_review_item(conn: sqlite3.Connection, doc_id: str, reason: str, priority: int = 0) -> str:
    """Enqueues an item into the manual review queue."""
    item_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO review_items (id, document_id, reason, priority, status, created_at) VALUES (?, ?, ?, ?, 'open', ?);",
        (item_id, doc_id, reason, priority, now)
    )
    return item_id


def list_review_queue(conn: sqlite3.Connection, status: str | None = None) -> list[dict]:
    """Retrieves pending items from the review queue with document metadata."""
    query = """
    SELECT r.id, r.document_id, r.reason, r.priority, r.status, r.assigned_to, r.created_at,
           d.original_filename, d.detected_type, a.id as application_id, a.registration_no, a.full_name
    FROM review_items r
    JOIN documents d ON r.document_id = d.id
    JOIN applications a ON d.application_id = a.id
    WHERE 1=1
    """
    params = []
    if status:
        query += " AND r.status = ?"
        params.append(status)
    query += " ORDER BY r.priority DESC, r.created_at ASC;"
    cursor = conn.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]


def record_field_review(conn: sqlite3.Connection, field_id: str, reviewer_id: str, decision: str, val: str | None, comment: str | None) -> None:
    """Records a reviewer's decision on an extracted field."""
    review_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO field_reviews (id, field_id, reviewer_id, decision, corrected_value, comment, reviewed_at, used_for_training)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1);
        """,
        (review_id, field_id, reviewer_id, decision, val, comment, now)
    )
    if decision == "corrected" and val is not None:
        conn.execute("UPDATE extracted_fields SET extracted_value = ?, status = 'match' WHERE id = ?;", (val, field_id))
    elif decision == "accepted":
        conn.execute("UPDATE extracted_fields SET status = 'match' WHERE id = ?;", (field_id,))
    elif decision == "rejected":
        conn.execute("UPDATE extracted_fields SET status = 'mismatch' WHERE id = ?;", (field_id,))


def get_document_fields(conn: sqlite3.Connection, doc_id: str) -> list[dict]:
    """Retrieves all extracted fields for the latest run of a document."""
    cursor = conn.execute(
        """
        SELECT f.* FROM extracted_fields f
        JOIN extraction_runs r ON f.run_id = r.id
        WHERE f.document_id = ? AND r.is_latest = 1;
        """,
        (doc_id,)
    )
    return [dict(r) for r in cursor.fetchall()]
