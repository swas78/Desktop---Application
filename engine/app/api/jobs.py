# For: Batch job scheduling, progress monitoring, and WebSocket event streaming
# Must never: Leave abandoned WebSocket connections unclosed or lose job state

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from engine.app.api.deps import get_current_user, require_role
from engine.app.db.connection import get_db
from engine.app.workers.queue import job_manager

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobCreatePayload(BaseModel):
    scope: str
    vacancy_id: str | None = None
    mode: str = "quick"


@router.post("")
async def create_job(payload: JobCreatePayload, user: dict = Depends(require_role(["admin", "officer"]))):
    """Enqueues documents for a batch verification job."""
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        doc_query = "SELECT d.id FROM documents d JOIN applications a ON d.application_id = a.id WHERE d.status IN ('uploaded', 'queued')"
        params = []
        if payload.vacancy_id:
            doc_query += " AND a.vacancy_id = ?"
            params.append(payload.vacancy_id)
        docs = conn.execute(doc_query, params).fetchall()
        total_count = len(docs)
        
        conn.execute(
            """
            INSERT INTO processing_jobs (id, scope, vacancy_id, mode, state, total, done, failed, created_by, created_at)
            VALUES (?, ?, ?, ?, 'queued', ?, 0, 0, ?, ?);
            """,
            (job_id, payload.scope, payload.vacancy_id, payload.mode, total_count, user["id"], now)
        )
        for d in docs:
            conn.execute(
                "INSERT INTO job_items (id, job_id, document_id, state) VALUES (?, ?, ?, 'queued');",
                (str(uuid.uuid4()), job_id, d["id"])
            )
            conn.execute("UPDATE documents SET status = 'queued' WHERE id = ?;", (d["id"],))

    await job_manager.start_job(job_id)
    return {"id": job_id, "total": total_count, "state": "running"}


@router.get("")
def list_jobs(_user: dict = Depends(get_current_user)):
    """Lists recent verification jobs."""
    with get_db() as conn:
        cur = conn.execute("SELECT * FROM processing_jobs ORDER BY created_at DESC LIMIT 50;")
        return [dict(r) for r in cur.fetchall()]


@router.get("/{job_id}")
def get_job(job_id: str, _user: dict = Depends(get_current_user)):
    """Retrieves current progress and metrics for a specific job."""
    with get_db() as conn:
        cur = conn.execute("SELECT * FROM processing_jobs WHERE id = ?;", (job_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Job not found"})
        return dict(row)


@router.post("/{job_id}/pause")
def pause_batch(job_id: str, _user: dict = Depends(require_role(["admin", "officer"]))):
    """Pauses active batch verification processing."""
    job_manager.pause_job(job_id)
    return {"status": "paused"}


@router.post("/{job_id}/resume")
def resume_batch(job_id: str, _user: dict = Depends(require_role(["admin", "officer"]))):
    """Resumes paused batch verification job."""
    job_manager.resume_job(job_id)
    return {"status": "resumed"}


@router.post("/{job_id}/cancel")
def cancel_batch(job_id: str, _user: dict = Depends(require_role(["admin", "officer"]))):
    """Cancels remaining documents in the batch."""
    job_manager.cancel_job(job_id)
    return {"status": "cancelled"}


@router.websocket("/ws/{job_id}")
async def websocket_job_progress(websocket: WebSocket, job_id: str):
    """Streams live batch progress events over WebSocket."""
    await websocket.accept()
    async def send_event(event: dict):
        if event.get("job_id") == job_id:
            await websocket.send_json(event)
    job_manager.register_listener(send_event)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
