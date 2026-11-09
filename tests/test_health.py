"""
Tests for GET /api/v1/health (Health & Diagnostics router).

Covers:
  - HTTP 200 response
  - Response schema (status / sqlite_wal / timestamp)
  - Valid ISO-8601 timestamp
  - sqlite_wal reflects the actual SQLite journal mode (not hardcoded)
"""
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Isolate the test database BEFORE importing src modules (DB path is read at import time).
TEST_DB = tempfile.mktemp(suffix="_health_test.db")
os.environ["INVENTORY_DB_PATH"] = TEST_DB

from fastapi.testclient import TestClient

from src.database import init_db, get_connection
from src.main import app


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()
    yield
    for ext in ("", "-wal", "-shm"):
        path = TEST_DB + ext
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _actual_journal_mode() -> str:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        return str(cur.fetchone()[0]).lower()
    finally:
        conn.close()


def test_health_returns_http_200(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_response_schema(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"status", "sqlite_wal", "timestamp"}
    assert body["status"] == "ok"
    assert isinstance(body["sqlite_wal"], bool)
    assert isinstance(body["timestamp"], str)


def test_health_timestamp_is_valid_iso8601(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    ts = response.json()["timestamp"]
    # ISO-8601 shape, e.g. 2026-11-10T01:23:45.678901+00:00 (or with 'Z')
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(\+\d{2}:\d{2}|-\d{2}:\d{2}|Z)?$", ts), ts
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    assert parsed.year >= 2026
    assert parsed.tzinfo is not None, "timestamp must carry timezone information"


def test_health_sqlite_wal_matches_actual_journal_mode(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    expected = _actual_journal_mode() == "wal"
    assert response.json()["sqlite_wal"] is expected


def test_health_database_is_in_wal_mode(client):
    # Project invariant: the configured SQLite database must run in WAL mode.
    assert _actual_journal_mode() == "wal"
    response = client.get("/api/v1/health")
    assert response.json()["sqlite_wal"] is True
