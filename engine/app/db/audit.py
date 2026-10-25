# For: Tamper-evident hash-chained audit logging service
# Must never: Update or delete existing audit entries or log raw PII

import hashlib
import json
from datetime import datetime, timezone
import sqlite3
from typing import Any


def calculate_audit_hash(prev_hash: str | None, payload_str: str) -> str:
    """Calculates SHA-256 hash chained to the previous record's hash."""
    combined = f"{prev_hash or ''}:{payload_str}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def log_audit_event(
    conn: sqlite3.Connection,
    action: str,
    user_id: str | None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> int:
    """Appends an immutable audit log entry chained with previous row's hash."""
    ts = datetime.now(timezone.utc).isoformat()
    details_json = json.dumps(details or {})
    
    cursor = conn.execute("SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1;")
    row = cursor.fetchone()
    prev_hash = row[0] if row else None
    
    payload_str = f"{ts}|{user_id or ''}|{action}|{entity_type or ''}|{entity_id or ''}|{details_json}"
    current_hash = calculate_audit_hash(prev_hash, payload_str)
    
    cursor = conn.execute(
        """
        INSERT INTO audit_log (ts, user_id, action, entity_type, entity_id, details_json, prev_hash, hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (ts, user_id, action, entity_type, entity_id, details_json, prev_hash, current_hash)
    )
    return cursor.lastrowid or 0


def verify_audit_chain(conn: sqlite3.Connection) -> bool:
    """Verifies that the entire audit log hash chain remains unbroken and untampered."""
    cursor = conn.execute("SELECT id, ts, user_id, action, entity_type, entity_id, details_json, prev_hash, hash FROM audit_log ORDER BY id ASC;")
    rows = cursor.fetchall()
    last_hash: str | None = None
    for r in rows:
        payload_str = f"{r['ts']}|{r['user_id'] or ''}|{r['action']}|{r['entity_type'] or ''}|{r['entity_id'] or ''}|{r['details_json']}"
        expected_hash = calculate_audit_hash(last_hash, payload_str)
        if r["hash"] != expected_hash or r["prev_hash"] != last_hash:
            return False
        last_hash = r["hash"]
    return True
