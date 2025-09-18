from fastapi.testclient import TestClient
from backend.app import app

def test_health_ok():
    with TestClient(app) as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json()["ok"] is True

