# For: Application eligibility evaluation API routes against vacancy criteria
# Must never: Overwrite candidate eligibility verdicts without saving rule reasons

import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from engine.app.api.deps import get_current_user, require_role
from engine.app.db.connection import get_db
from engine.app.db.repo_applications import get_application, get_vacancy
from engine.app.rules.eligibility import evaluate_application_eligibility

router = APIRouter(tags=["eligibility"])


@router.post("/applications/{app_id}/eligibility/evaluate")
def evaluate_single_application(app_id: str, _user: dict = Depends(get_current_user)):
    """Runs vacancy eligibility rules on a single application and stores verdict."""
    with get_db() as conn:
        app = get_application(conn, app_id)
        if not app:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Application not found"})
        vac = get_vacancy(conn, app["vacancy_id"])
        if not vac:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Vacancy not found"})
        
        rules = json.loads(vac["rules_json"])
        biodata = json.loads(app["biodata_json"]) if isinstance(app["biodata_json"], str) else app["biodata_json"]
        result = evaluate_application_eligibility(biodata, rules, vac["closing_date"])
        
        now = datetime.now(timezone.utc).isoformat()
        res_id = str(uuid.uuid4())
        conn.execute("UPDATE eligibility_results SET is_latest = 0 WHERE application_id = ?;", (app_id,))
        conn.execute(
            """
            INSERT INTO eligibility_results (id, application_id, vacancy_id, verdict, reasons_json, evaluated_at, is_latest)
            VALUES (?, ?, ?, ?, ?, ?, 1);
            """,
            (res_id, app_id, vac["id"], result["verdict"], json.dumps(result["reasons"]), now)
        )
        conn.execute("UPDATE applications SET eligibility = ? WHERE id = ?;", (result["verdict"], app_id))
        return result


@router.post("/vacancies/{vac_id}/eligibility/run")
def evaluate_vacancy_batch(vac_id: str, _user: dict = Depends(require_role(["admin", "officer"]))):
    """Evaluates eligibility for all applications enrolled in a specific vacancy."""
    with get_db() as conn:
        vac = get_vacancy(conn, vac_id)
        if not vac:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Vacancy not found"})
        rules = json.loads(vac["rules_json"])
        cur = conn.execute("SELECT id, biodata_json FROM applications WHERE vacancy_id = ?;", (vac_id,))
        apps = cur.fetchall()
        
        updated_count = 0
        now = datetime.now(timezone.utc).isoformat()
        for a in apps:
            biodata = json.loads(a["biodata_json"]) if isinstance(a["biodata_json"], str) else a["biodata_json"]
            result = evaluate_application_eligibility(biodata, rules, vac["closing_date"])
            conn.execute("UPDATE applications SET eligibility = ? WHERE id = ?;", (result["verdict"], a["id"]))
            conn.execute(
                """
                INSERT INTO eligibility_results (id, application_id, vacancy_id, verdict, reasons_json, evaluated_at, is_latest)
                VALUES (?, ?, ?, ?, ?, ?, 1);
                """,
                (str(uuid.uuid4()), a["id"], vac_id, result["verdict"], json.dumps(result["reasons"]), now)
            )
            updated_count += 1
        return {"status": "success", "evaluated": updated_count}
