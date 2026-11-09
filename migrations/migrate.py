"""
Simple SQLite WAL Schema Migration Runner
"""
import os
import sqlite3
from pathlib import Path

def run_migrations():
    db_file = os.environ.get("INVENTORY_DB_PATH", str(Path(__file__).resolve().parent.parent / "inventory.db"))
    migrations_dir = Path(__file__).resolve().parent / "versions"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    for sql_file in sorted(migrations_dir.glob("*.sql")):
        cur.executescript(sql_file.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    run_migrations()
    print("Migrations applied successfully.")
