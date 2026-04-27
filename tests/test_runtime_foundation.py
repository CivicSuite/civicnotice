from fastapi.testclient import TestClient

import civicnotice
from civicnotice.main import app


client = TestClient(app)


def test_package_version_is_010() -> None:
    assert civicnotice.__version__ == "0.1.0"


def test_root_endpoint_states_runtime_boundary() -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "CivicNotice"
    assert data["status"] == "notice compliance foundation"
    assert "official publication" in data["message"]
    assert "Post-v0.1.0 roadmap" in data["next_step"]


def test_health_endpoint_reports_versions() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "civicnotice"
    assert data["version"] == "0.1.0"
    assert data["civiccore_version"] == "0.2.0"
