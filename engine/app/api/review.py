# For: Review queue dispatching, claim handling, and reviewer workbench updates
# Must never: Overwrite ground-truth review labels without logging the reviewer ID

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from engine.app.api.deps import get_current_user
from engine.app.db.connection import get_db
from engine.app.db.repo_verification import (
    list_review_queue, record_field_review, get_document_fields
)
from engine.app.db.repo_applications import get_application

router = APIRouter(tags=["review"])


class FieldReviewPayload(BaseModel):
    decision: str
    corrected_value: str | None = None
    comment: str | None = None


@router.get("/review/queue")
def get_queue(status: str | None = "open", _user: dict = Depends(get_current_user)):
    """Retrieves list of documents requiring manual reviewer intervention."""
    with get_db() as conn:
        return list_review_queue(conn, status=status)


@router.post("/review/queue/{item_id}/claim")
def claim_item(item_id: str, user: dict = Depends(get_current_user)):
    """Assigns open review item to the authenticated reviewer."""
    with get_db() as conn:
        conn.execute(
            "UPDATE review_items SET status = 'claimed', assigned_to = ? WHERE id = ?;",
            (user["id"], item_id)
        )
    return {"status": "claimed", "item_id": item_id}


@router.patch("/fields/{field_id}")
def update_field_decision(field_id: str, payload: FieldReviewPayload, user: dict = Depends(get_current_user)):
    """Records human reviewer accept/correct/reject decision on an extracted field."""
    with get_db() as conn:
        record_field_review(
            conn, field_id, user["id"], payload.decision, payload.corrected_value, payload.comment
        )
    return {"status": "saved", "field_id": field_id}


@router.post("/review/queue/{item_id}/complete")
def complete_review_item(item_id: str, _user: dict = Depends(get_current_user)):
    """Marks review item complete and recomputes document and application status."""
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.execute("SELECT document_id FROM review_items WHERE id = ?;", (item_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Item not found"})
        doc_id = row["document_id"]
        
        # Check if all fields are now matches
        f_cur = conn.execute(
            """
            SELECT COUNT(CASE WHEN status != 'match' THEN 1 END) FROM extracted_fields f
            JOIN extraction_runs r ON f.run_id = r.id AND r.is_latest = 1
            WHERE f.document_id = ?;
            """,
            (doc_id,)
        )
        remaining_issues = f_cur.fetchone()[0]
        new_status = "verified" if remaining_issues == 0 else "mismatch"
        
        conn.execute("UPDATE documents SET status = ? WHERE id = ?;", (new_status, doc_id))
        conn.execute("UPDATE review_items SET status = 'completed', completed_at = ? WHERE id = ?;", (now, item_id))
    return {"status": "completed", "document_status": new_status}


@router.get("/review/items/{item_id}/detail")
def get_workbench_item_detail(item_id: str, _user: dict = Depends(get_current_user)):
    """Fetches full document, application, and fields with bounding boxes for workbench."""
    with get_db() as conn:
        cur = conn.execute("SELECT * FROM review_items WHERE id = ?;", (item_id,))
        item = cur.fetchone()
        if not item:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Review item not found"})
        
        doc_cur = conn.execute("SELECT * FROM documents WHERE id = ?;", (item["document_id"],))
        doc = dict(doc_cur.fetchone())
        app = get_application(conn, doc["application_id"])
        fields = get_document_fields(conn, doc["id"])
        
        return {
            "review_item": dict(item),
            "document": doc,
            "application": app,
            "fields": fields
        }
