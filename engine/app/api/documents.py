# For: Document attachment upload, encrypted storage retrieval, and page streaming
# Must never: Store plaintext sensitive documents outside the encrypted storage directory

import io
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response, StreamingResponse
from engine.app.api.deps import get_current_user
from engine.app.core.config import settings
from engine.app.core.security import encrypt_bytes, decrypt_bytes, compute_sha256
from engine.app.db.connection import get_db
from engine.app.db.repo_applications import create_document_record
from engine.app.db.audit import log_audit_event

router = APIRouter(tags=["documents"])


@router.post("/applications/{app_id}/documents")
async def upload_document(
    app_id: str,
    file: UploadFile = File(...),
    declared_type: str | None = Form(None),
    user: dict = Depends(get_current_user)
):
    """Uploads document file, encrypts bytes with AES-256-GCM, and attaches to application."""
    raw_bytes = await file.read()
    file_hash = compute_sha256(raw_bytes)
    encrypted_payload = encrypt_bytes(raw_bytes)
    
    file_id = str(uuid.uuid4())
    stored_path = settings.storage_dir / f"{file_id}.enc"
    stored_path.write_bytes(encrypted_payload)
    
    doc_payload = {
        "application_id": app_id,
        "original_filename": file.filename or "unknown",
        "mime_type": file.content_type or "application/octet-stream",
        "file_path": str(stored_path),
        "file_sha256": file_hash,
        "size_bytes": len(raw_bytes),
        "declared_type": declared_type,
        "uploaded_by": user["id"]
    }
    with get_db() as conn:
        doc = create_document_record(conn, doc_payload)
        log_audit_event(conn, "upload_document", user["id"], "document", doc["id"], {"filename": file.filename})
        return doc


@router.get("/documents/{doc_id}")
def get_document_meta(doc_id: str, _user: dict = Depends(get_current_user)):
    """Retrieves document record metadata and verification status."""
    with get_db() as conn:
        cur = conn.execute("SELECT * FROM documents WHERE id = ?;", (doc_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Document not found"})
        return dict(row)


@router.get("/documents/{doc_id}/file")
def stream_decrypted_document(doc_id: str, _user: dict = Depends(get_current_user)):
    """Decrypts and streams original file content directly to the client."""
    with get_db() as conn:
        cur = conn.execute("SELECT file_path, original_filename, mime_type FROM documents WHERE id = ?;", (doc_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Document not found"})
    
    file_path = Path(row["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Storage file not found on disk"})
    
    encrypted_bytes = file_path.read_bytes()
    decrypted_bytes = decrypt_bytes(encrypted_bytes)
    return Response(
        content=decrypted_bytes,
        media_type=row["mime_type"],
        headers={"Content-Disposition": f'inline; filename="{row["original_filename"]}"'}
    )
