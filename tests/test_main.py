"""
Automated Unit and Integration Tests Test Runner
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from main import InventoryApp

class TestLegacyInventoryApp(unittest.TestCase):
    def setUp(self):
        self.app = InventoryApp()

    def test_add_and_retrieve_item(self):
        ok = self.app.add_item("item-1", "Widgets", 15)
        self.assertTrue(ok)
        item = self.app.get_item("item-1")
        self.assertEqual(item["name"], "Widgets")
        self.assertEqual(item["quantity"], 15)

    def test_negative_quantity_rejected(self):
        ok = self.app.add_item("item-bad", "Broken", -5)
        self.assertFalse(ok)
        self.assertIsNone(self.app.get_item("item-bad"))

    def test_total_count(self):
        self.app.add_item("i1", "Box", 10)
        self.app.add_item("i2", "Bottle", 20)
        self.assertEqual(self.app.total_count(), 30)

if __name__ == "__main__":
    unittest.main()
