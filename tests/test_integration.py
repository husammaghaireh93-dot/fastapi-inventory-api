import os
import unittest
import tempfile
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

test_db = tempfile.mktemp(suffix="_integration.db")
os.environ["INVENTORY_DB_PATH"] = test_db

from fastapi.testclient import TestClient
from src.main import app
from src.database import init_db

class TestIntegrationWorkflows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        for ext in ["", "-wal", "-shm"]:
            f = test_db + ext
            if os.path.exists(f):
                os.remove(f)

    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["wal_mode"])

    def test_end_to_end_user_and_inventory_flow(self):
        # 1. Register User
        reg_res = self.client.post("/auth/register", json={"username": "prod_tester", "password": "securepassword123"})
        self.assertEqual(reg_res.status_code, 201)

        # 2. Login to obtain Bearer Token
        login_res = self.client.post("/auth/login", json={"username": "prod_tester", "password": "securepassword123"})
        self.assertEqual(login_res.status_code, 200)
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create Category
        cat_res = self.client.post("/categories", json={"name": "Displays", "description": "High-res monitors"}, headers=headers)
        self.assertEqual(cat_res.status_code, 201)
        cat_id = cat_res.json()["id"]

        # 4. Create Inventory Item
        item_res = self.client.post("/items", json={
            "sku": "SKU-MONITOR-4K-PRO",
            "name": "4K Ultra-HD Monitor Pro",
            "price": 349.99,
            "quantity": 25,
            "category_id": cat_id,
            "reorder_threshold": 5
        }, headers=headers)
        self.assertEqual(item_res.status_code, 201)
        item_id = item_res.json()["id"]

        # 5. Fetch Item
        get_res = self.client.get(f"/items/{item_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["name"], "4K Ultra-HD Monitor Pro")

        # 6. Adjust Stock Atomically
        adj_res = self.client.post(f"/items/{item_id}/adjust-stock", json={
            "change_amount": 10,
            "reason": "Shipment arrived"
        }, headers=headers)
        self.assertEqual(adj_res.status_code, 200)
        self.assertEqual(adj_res.json()["new_quantity"], 35)

        # 7. Check Aggregated Stats
        stats_res = self.client.get("/stats")
        self.assertEqual(stats_res.status_code, 200)
        self.assertGreaterEqual(stats_res.json()["total_quantity"], 35)
