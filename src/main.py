"""
FastAPI Inventory Management Service with SQLite WAL Mode
Generated & Orchestrated via NOVA Universal Dispatcher & Antigravity Engine.
"""
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, get_connection
from .routers.auth_router import router as auth_router
from .routers.inventory_router import router as inventory_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite WAL tables exist
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

# Compatibility class for legacy unit tests
class InventoryApp:
    def __init__(self):
        self.items = {}

    def add_item(self, item_id: str, name: str, quantity: int) -> bool:
        if quantity < 0:
            return False
        self.items[item_id] = {"name": name, "quantity": quantity}
        return True

    def get_item(self, item_id: str):
        return self.items.get(item_id)

    def total_count(self) -> int:
        return sum(item["quantity"] for item in self.items.values())
