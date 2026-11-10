"""
Health & Diagnostics endpoints.

Exposes GET /api/v1/health which reports service status, the actual
SQLite journal mode of the configured database (WAL or otherwise), and
an ISO-8601 system timestamp. No values are hardcoded: the journal mode
is read live from the database on every request.
"""
from datetime import datetime, timezone

from fastapi import APIRouter

from ..database import get_connection

router = APIRouter(prefix="/api/v1", tags=["Health"])


def _read_journal_mode() -> str:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        row = cur.fetchone()
        if row is None or row[0] is None:
            raise RuntimeError("Unable to read SQLite journal mode (PRAGMA journal_mode returned no row)")
        return str(row[0]).lower()
    finally:
        conn.close()


@router.get("/health")
def health_check():
    journal_mode = _read_journal_mode()
    return {
        "status": "ok",
        # Derived from the live PRAGMA journal_mode, never hardcoded.
        "sqlite_wal": journal_mode == "wal",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
