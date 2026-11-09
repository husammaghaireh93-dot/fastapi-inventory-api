import os
import unittest
import tempfile
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

test_db = tempfile.mktemp(suffix="_wal.db")
os.environ["INVENTORY_DB_PATH"] = test_db

from src.database import init_db, get_connection

class TestWalConcurrency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    @classmethod
    def tearDownClass(cls):
        for ext in ["", "-wal", "-shm"]:
            f = test_db + ext
            if os.path.exists(f):
                os.remove(f)

    def test_wal_pragma_enabled(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        mode = cur.fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal", "Database must operate in SQLite WAL mode")
