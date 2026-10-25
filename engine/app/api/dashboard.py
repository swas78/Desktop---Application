# For: Dashboard metrics, ledger analytics, and verification quality reporting
# Must never: Expose individual candidate identities through statistical aggregates

from fastapi import APIRouter, Depends
from engine.app.api.deps import get_current_user
from engine.app.db.connection import get_db
from engine.app.db.repo_dashboard import (
    get_dashboard_summary, get_mismatches_summary, get_accuracy_metrics
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_summary(_user: dict = Depends(get_current_user)):
    """Computes headline verification throughput, review rate, and ledger breakdown."""
    with get_db() as conn:
        return get_dashboard_summary(conn)


@router.get("/mismatches")
def get_mismatches(_user: dict = Depends(get_current_user)):
    """Returns top discrepancy occurrences grouped by field name and reason."""
    with get_db() as conn:
        return get_mismatches_summary(conn)


@router.get("/accuracy")
def get_accuracy(_user: dict = Depends(get_current_user)):
    """Returns measured accuracy per field and document type with sample sizes."""
    with get_db() as conn:
        return get_accuracy_metrics(conn)


@router.get("/timeseries")
def get_timeseries(_user: dict = Depends(get_current_user)):
    """Generates verification throughput time-series for trend charts."""
    with get_db() as conn:
        cur = conn.execute(
            """
            SELECT substr(started_at, 1, 10) as day, COUNT(*) as processed, AVG(total_ms) as avg_ms
            FROM extraction_runs
            WHERE is_latest = 1
            GROUP BY day
            ORDER BY day ASC LIMIT 30;
            """
        )
        return [{"date": r["day"], "processed": r["processed"], "avg_ms": round(r["avg_ms"] or 0, 1)} for r in cur.fetchall()]
