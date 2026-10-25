# For: Candidate application browsing, single entry, bulk import, and alert export
# Must never: Expose unmasked application details without authenticated session

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from engine.app.api.deps import get_current_user, require_role
from engine.app.db.connection import get_db
from engine.app.db.repo_applications import (
    list_applications, get_application, create_application
)
from engine.app.db.audit import log_audit_event

router = APIRouter(prefix="/applications", tags=["applications"])


class ApplicationCreatePayload(BaseModel):
    registration_no: str
    vacancy_id: str
    biodata: dict


@router.get("")
def get_applications(
    vacancy_id: str | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None),
    _user: dict = Depends(get_current_user)
):
    """Lists applications matching search filters."""
    with get_db() as conn:
        return list_applications(conn, vacancy_id=vacancy_id, status=status, search=search)


@router.post("")
def add_application(payload: ApplicationCreatePayload, user: dict = Depends(require_role(["admin", "officer"]))):
    """Creates a single candidate application record."""
    with get_db() as conn:
        app = create_application(conn, payload.model_dump())
        log_audit_event(conn, "create_application", user["id"], "application", app["id"], {"reg_no": app["registration_no"]})
        return app


@router.get("/{app_id}")
def get_single_application(app_id: str, _user: dict = Depends(get_current_user)):
    """Retrieves single application with attached documents."""
    with get_db() as conn:
        app = get_application(conn, app_id)
        if not app:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Application not found"})
        return app


@router.post("/import")
def import_applications(payload: dict, user: dict = Depends(require_role(["admin", "officer"]))):
    """Imports candidate application records from tabular CSV or JSON rows."""
    rows = payload.get("rows", [])
    vacancy_id = payload.get("vacancy_id", "")
    created_count = 0
    with get_db() as conn:
        for r in rows:
            reg_no = r.get("registration_no") or r.get("reg_no")
            if not reg_no:
                continue
            app_data = {
                "registration_no": reg_no,
                "vacancy_id": vacancy_id,
                "biodata": r
            }
            create_application(conn, app_data)
            created_count += 1
        log_audit_event(conn, "bulk_import", user["id"], "import_batch", None, {"count": created_count})
    return {"status": "success", "imported": created_count}


@router.post("/{app_id}/alerts/export")
def export_application_alerts(app_id: str, _user: dict = Depends(get_current_user)):
    """Generates candidate-facing discrepancy alert message for correction notifications."""
    with get_db() as conn:
        app = get_application(conn, app_id)
        if not app:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Application not found"})
        cur = conn.execute(
            """
            SELECT f.field_name, f.extracted_value, f.expected_value, f.reason
            FROM extracted_fields f
            JOIN documents d ON f.document_id = d.id
            JOIN extraction_runs r ON f.run_id = r.id AND r.is_latest = 1
            WHERE d.application_id = ? AND f.status = 'mismatch';
            """,
            (app_id,)
        )
        mismatches = cur.fetchall()
        alerts = [
            {
                "field": m["field_name"],
                "message": f"Entered {m['expected_value']} but document shows {m['extracted_value']}. Please review your application."
            }
            for m in mismatches
        ]
        return {"registration_no": app["registration_no"], "alerts": alerts}
