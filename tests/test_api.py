import os
import unittest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
test_db = tempfile.mktemp(suffix="_api.db")
os.environ["INVENTORY_DB_PATH"] = test_db

from fastapi.testclient import TestClient
from src.main import app
from src.database import init_db

class TestApiEndpoints(unittest.TestCase):
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

    def test_user_flow_and_inventory(self):
        # Register user
        reg_res = self.client.post("/auth/register", json={"username": "operator", "password": "securepassword123"})
        self.assertEqual(reg_res.status_code, 201)

        # Login
        login_res = self.client.post("/auth/login", json={"username": "operator", "password": "securepassword123"})
        self.assertEqual(login_res.status_code, 200)
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create Item
        item_res = self.client.post("/items", json={
            "sku": "SKU-MONITOR-4K",
            "name": "4K Ultra-HD Monitor",
            "price": 299.99,
            "quantity": 15,
            "reorder_threshold": 3
        }, headers=headers)
        self.assertEqual(item_res.status_code, 201)
        item_id = item_res.json()["id"]

        # Adjust stock
        adj_res = self.client.post(f"/items/{item_id}/adjust-stock", json={
            "change_amount": 5,
            "reason": "Restocked shipment"
        }, headers=headers)
        self.assertEqual(adj_res.status_code, 200)
        self.assertEqual(adj_res.json()["new_quantity"], 20)

        # Read stats
        stats_res = self.client.get("/stats")
        self.assertEqual(stats_res.status_code, 200)
        self.assertEqual(stats_res.json()["total_quantity"], 20)
