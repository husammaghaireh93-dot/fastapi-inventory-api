"""
FastAPI Application Initialization and Route Smoke Tests
"""
import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from src.main import app

class TestMainApp(unittest.TestCase):
    def test_app_metadata(self):
        self.assertEqual(app.title, "NOVA Production Inventory Management API")
        self.assertEqual(app.version, "1.0.0")

    def test_routes_registered(self):
        paths = []
        for r in app.routes:
            if hasattr(r, "path"):
                paths.append(r.path)
            elif hasattr(r, "routes"):
                for sub in r.routes:
                    if hasattr(sub, "path"):
                        paths.append(sub.path)
        self.assertIn("/health", paths)
        self.assertIn("/docs", paths)

if __name__ == "__main__":
    unittest.main()
