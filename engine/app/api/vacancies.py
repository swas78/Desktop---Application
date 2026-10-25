# For: Vacancy recruitment criteria management API endpoints
# Must never: Expose vacancy modification to non-admin roles without validation

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from engine.app.api.deps import get_current_user, require_role
from engine.app.db.connection import get_db
from engine.app.db.repo_applications import list_vacancies, get_vacancy, create_vacancy
from engine.app.db.audit import log_audit_event

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


class VacancyCreatePayload(BaseModel):
    advt_no: str
    post_name: str
    closing_date: str
    rules: dict


@router.get("")
def get_all_vacancies(_user: dict = Depends(get_current_user)):
    """Lists all recruitment vacancies."""
    with get_db() as conn:
        return list_vacancies(conn)


@router.post("")
def add_vacancy(payload: VacancyCreatePayload, user: dict = Depends(require_role(["admin"]))):
    """Creates a new vacancy and logs audit event."""
    with get_db() as conn:
        vac = create_vacancy(conn, payload.model_dump(), user["id"])
        log_audit_event(conn, "create_vacancy", user["id"], "vacancy", vac["id"], {"advt_no": vac["advt_no"]})
        return vac


@router.get("/{vacancy_id}")
def get_single_vacancy(vacancy_id: str, _user: dict = Depends(get_current_user)):
    """Retrieves single vacancy specification."""
    with get_db() as conn:
        vac = get_vacancy(conn, vacancy_id)
        if not vac:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Vacancy not found"})
        return vac
