# For: Verification outcome and candidate shortlist report generation
# Must never: Generate reports containing unverified internal database IDs

import io
import uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl
from engine.app.api.deps import get_current_user
from engine.app.core.config import settings
from engine.app.db.connection import get_db

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportCreatePayload(BaseModel):
    type: str  # "verification" or "shortlist"
    format: str  # "pdf" or "xlsx"
    vacancy_id: str | None = None


def generate_pdf_report(records: list[dict], title: str) -> bytes:
    """Generates a clean PDF verification report using ReportLab."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, f"RAC DRDO - {title}")
    c.setFont("Helvetica", 10)
    c.drawString(50, 730, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    y = 690
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Reg No")
    c.drawString(160, y, "Candidate Name")
    c.drawString(330, y, "Status")
    c.drawString(450, y, "Eligibility")
    c.line(50, y - 5, 550, y - 5)
    y -= 25
    
    c.setFont("Helvetica", 10)
    for r in records[:30]:
        c.drawString(50, y, str(r["registration_no"]))
        c.drawString(160, y, str(r["full_name"])[:25])
        c.drawString(330, y, str(r["status"]))
        c.drawString(450, y, str(r["eligibility"]))
        y -= 20
        if y < 50:
            c.showPage()
            y = 720
    c.save()
    return buffer.getvalue()


def generate_excel_report(records: list[dict]) -> bytes:
    """Generates Excel workbook report."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Verification Summary"
    ws.append(["Registration No", "Full Name", "Category", "Verification Status", "Eligibility"])
    for r in records:
        ws.append([r["registration_no"], r["full_name"], r.get("category", "UR"), r["status"], r["eligibility"]])
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


@router.post("")
def create_report(payload: ReportCreatePayload, user: dict = Depends(get_current_user)):
    """Generates official verification outcome report as PDF or Excel."""
    with get_db() as conn:
        q = "SELECT registration_no, full_name, category, status, eligibility FROM applications WHERE 1=1"
        params = []
        if payload.vacancy_id:
            q += " AND vacancy_id = ?"
            params.append(payload.vacancy_id)
        rows = [dict(r) for r in conn.execute(q, params).fetchall()]
        
        rep_id = str(uuid.uuid4())
        file_name = f"report_{rep_id}.{payload.format}"
        file_path = settings.storage_dir / file_name
        
        if payload.format == "pdf":
            data_bytes = generate_pdf_report(rows, f"{payload.type.title()} Report")
        else:
            data_bytes = generate_excel_report(rows)
            
        file_path.write_bytes(data_bytes)
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO reports (id, type, format, file_path, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?);",
            (rep_id, payload.type, payload.format, str(file_path), user["id"], now)
        )
        return {"id": rep_id, "filename": file_name}


@router.get("/{report_id}/download")
def download_report(report_id: str, _user: dict = Depends(get_current_user)):
    """Downloads generated PDF or Excel report."""
    with get_db() as conn:
        cur = conn.execute("SELECT file_path, format FROM reports WHERE id = ?;", (report_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Report not found"})
        fpath = Path(row["file_path"])
        if not fpath.exists():
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "File not on disk"})
        media = "application/pdf" if row["format"] == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return Response(content=fpath.read_bytes(), media_type=media)
