"""
CRUD and Transaction management with SQLite WAL transactions.
"""
import sqlite3
from typing import List, Optional, Dict, Any
from .database import get_connection
from .auth import hash_password, verify_password

def create_user(username: str, password: str, role: str = "user") -> Optional[int]:
    conn = get_connection()
    cur = conn.cursor()
    pwd_hash = hash_password(password)
    try:
        cur.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?);", (username, pwd_hash, role))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?;", (username,))
    row = cur.fetchone()
    conn.close()
    if row and verify_password(password, row["password_hash"]):
        return {"id": row["id"], "username": row["username"], "role": row["role"]}
    return None

def create_category(name: str, description: Optional[str] = None) -> Optional[int]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO categories (name, description) VALUES (?, ?);", (name, description))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_categories() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, description FROM categories ORDER BY name ASC;")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_item(sku: str, name: str, price: float, quantity: int, category_id: Optional[int] = None, reorder_threshold: int = 5) -> Optional[int]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT INTO items (sku, name, price, quantity, category_id, reorder_threshold)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (sku, name, price, quantity, category_id, reorder_threshold))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_items(category_id: Optional[int] = None, search: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM items WHERE 1=1"
    params = []
    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)
    if search:
        query += " AND (name LIKE ? OR sku LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY id DESC LIMIT ? OFFSET ?;"
    params.extend([limit, skip])
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE id = ?;", (item_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

ALLOWED_UPDATE_FIELDS = {"sku", "name", "description", "category", "unit_price", "reorder_level"}

def update_item(item_id: int, fields: Dict[str, Any]) -> bool:
    filtered_fields = {k: v for k, v in fields.items() if k in ALLOWED_UPDATE_FIELDS}
    if not filtered_fields:
        return False
    conn = get_connection()
    cur = conn.cursor()
    set_clauses = [f"{k} = ?" for k in filtered_fields.keys()]
    values = list(filtered_fields.values()) + [item_id]
    query = f"UPDATE items SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?;"  # nosec B608
    cur.execute(query, values)
    conn.commit()
    updated = (cur.rowcount > 0)
    conn.close()
    return updated

def delete_item(item_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = ?;", (item_id,))
    conn.commit()
    deleted = (cur.rowcount > 0)
    conn.close()
    return deleted

def adjust_stock(item_id: int, change_amount: int, reason: str = "Adjustment") -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("BEGIN IMMEDIATE;")
        cur.execute("SELECT id, quantity FROM items WHERE id = ?;", (item_id,))
        row = cur.fetchone()
        if not row:
            conn.rollback()
            return None
        current_qty = row["quantity"]
        new_qty = current_qty + change_amount
        if new_qty < 0:
            conn.rollback()
            return None
        cur.execute("UPDATE items SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (new_qty, item_id))
        cur.execute("""
        INSERT INTO inventory_transactions (item_id, change_amount, previous_quantity, new_quantity, reason)
        VALUES (?, ?, ?, ?, ?);
        """, (item_id, change_amount, current_qty, new_qty, reason))
        conn.commit()
        return {"item_id": item_id, "previous_quantity": current_qty, "new_quantity": new_qty, "change_amount": change_amount}
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(quantity), 0) as total_qty, COALESCE(SUM(price * quantity), 0.0) as val FROM items;")
    r1 = cur.fetchone()
    cur.execute("SELECT COUNT(*) as low_cnt FROM items WHERE quantity <= reorder_threshold;")
    r2 = cur.fetchone()
    conn.close()
    return {
        "total_items": r1["cnt"],
        "total_quantity": r1["total_qty"],
        "total_valuation": round(r1["val"], 2),
        "low_stock_items": r2["low_cnt"]
    }
