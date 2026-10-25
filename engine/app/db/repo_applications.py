# For: Vacancy definitions, candidate applications, and document attachment storage
# Must never: Delete applicant files without writing to the tamper-evident audit log

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any


def list_vacancies(conn: sqlite3.Connection) -> list[dict]:
    """Lists all active and archived recruitment vacancies."""
    cursor = conn.execute("SELECT * FROM vacancies ORDER BY created_at DESC;")
    return [dict(r) for r in cursor.fetchall()]


def get_vacancy(conn: sqlite3.Connection, vacancy_id: str) -> dict | None:
    """Retrieves vacancy details by ID."""
    cursor = conn.execute("SELECT * FROM vacancies WHERE id = ?;", (vacancy_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def create_vacancy(conn: sqlite3.Connection, data: dict, user_id: str) -> dict:
    """Creates a new vacancy with its rules specification."""
    vac_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO vacancies (id, advt_no, post_name, closing_date, rules_json, status, created_by, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        (vac_id, data["advt_no"], data["post_name"], data["closing_date"], json.dumps(data["rules"]), "active", user_id, now)
    )
    return get_vacancy(conn, vac_id) or {}


def list_applications(conn: sqlite3.Connection, vacancy_id: str | None = None, status: str | None = None, search: str | None = None) -> list[dict]:
    """Lists applications with optional search and status filtering."""
    query = "SELECT * FROM applications WHERE 1=1"
    params: list[Any] = []
    if vacancy_id:
        query += " AND vacancy_id = ?"
        params.append(vacancy_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND (full_name LIKE ? OR registration_no LIKE ?)"
        wild = f"%{search}%"
        params.extend([wild, wild])
    query += " ORDER BY created_at DESC;"
    cursor = conn.execute(query, params)
    return [dict(r) for r in cursor.fetchall()]


def get_application(conn: sqlite3.Connection, app_id: str) -> dict | None:
    """Retrieves single application with attached documents."""
    cursor = conn.execute("SELECT * FROM applications WHERE id = ?;", (app_id,))
    row = cursor.fetchone()
    if not row:
        return None
    app_dict = dict(row)
    doc_cursor = conn.execute("SELECT * FROM documents WHERE application_id = ? ORDER BY uploaded_at ASC;", (app_id,))
    app_dict["documents"] = [dict(d) for d in doc_cursor.fetchall()]
    return app_dict


def create_application(conn: sqlite3.Connection, data: dict) -> dict:
    """Inserts a new candidate application with biodata."""
    app_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    bio = data.get("biodata", {})
    conn.execute(
        """
        INSERT INTO applications (id, registration_no, vacancy_id, full_name, father_name, dob, category, is_pwd, biodata_json, status, eligibility, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            app_id, data["registration_no"], data["vacancy_id"], bio.get("fullName", data.get("full_name", "")),
            bio.get("fatherName"), bio.get("dob"), bio.get("category"), 1 if bio.get("pwd") else 0,
            json.dumps(bio), "pending", "unknown", now
        )
    )
    return get_application(conn, app_id) or {}


def create_document_record(conn: sqlite3.Connection, data: dict) -> dict:
    """Stores a new document attachment record."""
    doc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO documents (id, application_id, original_filename, mime_type, file_path, file_sha256, size_bytes, page_count, declared_type, status, uploaded_by, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            doc_id, data["application_id"], data["original_filename"], data["mime_type"],
            data["file_path"], data["file_sha256"], data["size_bytes"], data.get("page_count", 1),
            data.get("declared_type"), "uploaded", data.get("uploaded_by"), now
        )
    )
    cursor = conn.execute("SELECT * FROM documents WHERE id = ?;", (doc_id,))
    return dict(cursor.fetchone())
