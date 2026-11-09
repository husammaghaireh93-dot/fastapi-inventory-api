"""
FastAPI Inventory Management Service with SQLite WAL Mode
Orchestrated via NOVA Universal Dispatcher & Antigravity Engine.
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure package context
pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from src.database import init_db, get_connection
from src.routers.auth_router import router as auth_router
from src.routers.inventory_router import router as inventory_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="NOVA Production Inventory Management API",
    description="High-concurrency REST API backed by SQLite WAL mode, Bearer auth, and comprehensive test suites.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(inventory_router)

@app.get("/health", tags=["Health"])
def health_check():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode;")
    mode = cur.fetchone()[0]
    conn.close()
    return {
        "status": "healthy",
        "wal_mode": (mode.lower() == "wal"),
        "journal_mode": mode,
        "engine": "FastAPI + SQLite WAL",
        "docs": "/docs"
    }
