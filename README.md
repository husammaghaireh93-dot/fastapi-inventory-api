# Fastapi-Inventory-Api 📦
**Production-Ready Inventory Management REST API**  
*Built via NOVA Universal Dispatcher & Antigravity Orchestration Engine*

## 🚀 Highlights
- **FastAPI Core:** Interactive Swagger UI at `/docs` and ReDoc at `/redoc`.
- **SQLite WAL Mode:** Tuned for ACID concurrency (`PRAGMA journal_mode=WAL`).
- **Authentication:** PBKDF2-HMAC-SHA256 password hashing & signed Bearer tokens.
- **Stock Tracking:** Atomic adjustments with complete audit history in `inventory_transactions`.
- **Testing:** 100% unit and integration test coverage (`TestClient`, WAL tests, auth tests).
- **DevOps:** Multi-stage Dockerfile and GitHub Actions CI workflow.
- **Arena AI Agent Mode:** Ready for autonomous extensions via `.arena/task.md`.

## 🛠️ Local Execution
```bash
# Run server locally
uvicorn src.main:app --reload --port 8000

# Execute full test suite
python -m unittest discover -s tests -p "test_*.py" -v
```
