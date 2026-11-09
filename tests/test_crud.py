import os
import unittest
import tempfile
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

test_db = tempfile.mktemp(suffix=".db")
os.environ["INVENTORY_DB_PATH"] = test_db

from src.database import init_db
from src import crud

class TestCrudOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(test_db):
            os.remove(test_db)

    def test_item_lifecycle(self):
        cat_id = crud.create_category("Electronics", "Gadgets and tech")
        self.assertIsNotNone(cat_id)

        item_id = crud.create_item("SKU-TEST-001", "Keyboard", 49.99, 10, category_id=cat_id)
        self.assertIsNotNone(item_id)

        item = crud.get_item_by_id(item_id)
        self.assertEqual(item["name"], "Keyboard")
        self.assertEqual(item["quantity"], 10)

        # Stock adjustment
        adj = crud.adjust_stock(item_id, -3, "Sold 3 units")
        self.assertEqual(adj["new_quantity"], 7)

        # Prevent negative quantity
        bad_adj = crud.adjust_stock(item_id, -20, "Overdrawn")
        self.assertIsNone(bad_adj)

        # Stats check
        stats = crud.get_stats()
        self.assertGreaterEqual(stats["total_items"], 1)
        self.assertGreaterEqual(stats["total_quantity"], 7)
