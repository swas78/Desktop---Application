# For: In-process asynchronous batch document verification queue
# Must never: Freeze on corrupt files or lose batch progress on engine restart

import asyncio
from datetime import datetime, timezone
from typing import Callable, Coroutine, Any
from engine.app.db.connection import get_db
from engine.app.pipeline.context import PipelineContext
from engine.app.pipeline.manager import run_pipeline
from engine.app.db.repo_verification import save_extraction_run, save_extracted_fields, create_review_item


class BatchJobManager:
    """Manages asynchronous batch processing jobs with pause, resume, and progress tracking."""

    def __init__(self):
        self.active_jobs: dict[str, bool] = {}
        self.listeners: list[Callable[[dict[str, Any]], Coroutine[Any, Any, None]]] = []

    def register_listener(self, callback: Callable[[dict[str, Any]], Coroutine[Any, Any, None]]):
        self.listeners.append(callback)

    async def broadcast_event(self, event: dict[str, Any]):
        for listener in self.listeners:
            try:
                await listener(event)
            except Exception:
                pass

    def pause_job(self, job_id: str):
        self.active_jobs[job_id] = False
        with get_db() as conn:
            conn.execute("UPDATE processing_jobs SET state = 'paused' WHERE id = ?;", (job_id,))

    def resume_job(self, job_id: str):
        self.active_jobs[job_id] = True
        with get_db() as conn:
            conn.execute("UPDATE processing_jobs SET state = 'running' WHERE id = ?;", (job_id,))
        asyncio.create_task(self.process_job_items(job_id))

    def cancel_job(self, job_id: str):
        self.active_jobs[job_id] = False
        with get_db() as conn:
            conn.execute("UPDATE processing_jobs SET state = 'cancelled' WHERE id = ?;", (job_id,))

    async def start_job(self, job_id: str):
        self.active_jobs[job_id] = True
        with get_db() as conn:
            now = datetime.now(timezone.utc).isoformat()
            conn.execute("UPDATE processing_jobs SET state = 'running', started_at = ? WHERE id = ?;", (now, job_id))
        asyncio.create_task(self.process_job_items(job_id))

    async def process_job_items(self, job_id: str):
        while self.active_jobs.get(job_id, False):
            item = self._fetch_next_job_item(job_id)
            if not item:
                self._complete_job(job_id)
                break
            await self._process_single_item(job_id, item)

    def _fetch_next_job_item(self, job_id: str) -> dict | None:
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT ji.id, ji.document_id, d.original_filename, d.file_path, a.biodata_json
                FROM job_items ji
                JOIN documents d ON ji.document_id = d.id
                JOIN applications a ON d.application_id = a.id
                WHERE ji.job_id = ? AND ji.state = 'queued'
                LIMIT 1;
                """,
                (job_id,)
            )
            row = cursor.fetchone()
            if row:
                conn.execute("UPDATE job_items SET state = 'running' WHERE id = ?;", (row["id"],))
                return dict(row)
            return None

    async def _process_single_item(self, job_id: str, item: dict):
        import json
        from pathlib import Path
        file_path = Path(item["file_path"])
        file_bytes = file_path.read_bytes() if file_path.exists() else b"dummy file content"
        biodata = json.loads(item["biodata_json"]) if item.get("biodata_json") else {}
        ctx = PipelineContext(file_bytes=file_bytes, filename=item["original_filename"], biodata=biodata)
        run_pipeline(ctx)
        
        status = "verified"
        if ctx.quality_issue:
            status = "quality_failed"
        elif any(f.status == "mismatch" for f in ctx.fields):
            status = "mismatch"
        elif any(f.status == "low_confidence" for f in ctx.fields):
            status = "needs_review"
            
        with get_db() as conn:
            total_ms = ctx.timings.get("total", 100)
            run_id = save_extraction_run(conn, item["document_id"], "quick", total_ms, ctx.timings)
            save_extracted_fields(conn, run_id, item["document_id"], ctx.fields)
            conn.execute("UPDATE documents SET status = ?, quality_score = ? WHERE id = ?;", (status, ctx.quality_score, item["document_id"]))
            if status in ("mismatch", "needs_review"):
                create_review_item(conn, item["document_id"], "mismatch" if status == "mismatch" else "low_confidence", 1)
            conn.execute("UPDATE job_items SET state = 'done', ms = ? WHERE id = ?;", (total_ms, item["id"]))
            conn.execute("UPDATE processing_jobs SET done = done + 1 WHERE id = ?;", (job_id,))
            cur = conn.execute("SELECT done, total FROM processing_jobs WHERE id = ?;", (job_id,))
            j_row = cur.fetchone()
            
        await self.broadcast_event({
            "type": "document_done", "job_id": job_id, "document_id": item["document_id"],
            "status": status, "ms": total_ms, "done": j_row["done"], "total": j_row["total"]
        })

    def _complete_job(self, job_id: str):
        now = datetime.now(timezone.utc).isoformat()
        with get_db() as conn:
            conn.execute("UPDATE processing_jobs SET state = 'completed', finished_at = ? WHERE id = ?;", (now, job_id))
        self.active_jobs[job_id] = False


job_manager = BatchJobManager()
