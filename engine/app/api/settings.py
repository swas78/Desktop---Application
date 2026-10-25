# For: System administration, settings configuration, and audit trail inspection
# Must never: Expose system settings modification to unauthorized user roles

import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from engine.app.api.deps import get_current_user, require_role
from engine.app.db.connection import get_db
from engine.app.db.repo_auth import list_users, create_user
from engine.app.db.audit import verify_audit_chain, log_audit_event

router = APIRouter(tags=["settings"])


class UserCreatePayload(BaseModel):
    username: str
    password: str
    full_name: str
    role: str


@router.get("/health")
def health_check():
    """Returns engine operational status and model readiness."""
    with get_db() as conn:
        audit_valid = verify_audit_chain(conn)
    return {
        "status": "healthy",
        "engine": "FastAPI",
        "version": "1.0.0",
        "audit_integrity": audit_valid,
        "models_loaded": True
    }


@router.get("/settings")
def get_settings(_user: dict = Depends(get_current_user)):
    """Retrieves current verification thresholds and system settings."""
    with get_db() as conn:
        rows = conn.execute("SELECT key, value_json FROM settings;").fetchall()
        return {r["key"]: json.loads(r["value_json"]) for r in rows}


@router.put("/settings")
def update_settings(payload: dict, user: dict = Depends(require_role(["admin"]))):
    """Updates system thresholds and records change in audit log."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        for k, v in payload.items():
            conn.execute(
                "INSERT INTO settings (key, value_json, updated_by, updated_at) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json, updated_at = excluded.updated_at;",
                (k, json.dumps(v), user["id"], now)
            )
        log_audit_event(conn, "update_settings", user["id"], "settings", None, payload)
    return {"status": "saved"}


@router.get("/users")
def get_user_list(_user: dict = Depends(require_role(["admin"]))):
    """Lists system operators and roles."""
    with get_db() as conn:
        return list_users(conn)


@router.post("/users")
def add_new_user(payload: UserCreatePayload, user: dict = Depends(require_role(["admin"]))):
    """Provisions a new user account."""
    with get_db() as conn:
        new_u = create_user(conn, payload.model_dump())
        log_audit_event(conn, "create_user", user["id"], "user", new_u["id"], {"username": payload.username})
        return new_u


@router.get("/audit")
def get_audit_trail(_user: dict = Depends(require_role(["admin"]))):
    """Returns tamper-evident audit log with hash-chain verification."""
    with get_db() as conn:
        chain_ok = verify_audit_chain(conn)
        cur = conn.execute(
            """
            SELECT a.id, a.ts, a.user_id, u.username, a.action, a.entity_type, a.entity_id, a.details_json, a.hash
            FROM audit_log a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.id DESC LIMIT 100;
            """
        )
        entries = [dict(r) for r in cur.fetchall()]
        return {"chain_valid": chain_ok, "entries": entries}


@router.get("/models")
def get_models(_user: dict = Depends(get_current_user)):
    """Lists installed models and active versions."""
    return [
        {"name": "ocr_engine", "version": "1.0.0", "status": "active"},
        {"name": "document_classifier", "version": "1.0.0", "status": "active"},
        {"name": "layout_extractor", "version": "1.0.0", "status": "active"},
        {"name": "authenticity_analyzer", "version": "1.0.0", "status": "active"}
    ]
