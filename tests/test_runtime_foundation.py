from fastapi.testclient import TestClient

import civicnotice
from civicnotice.main import app


client = TestClient(app)


def test_package_version_is_012() -> None:
    assert civicnotice.__version__ == "0.1.2"


def test_root_endpoint_states_runtime_boundary() -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "CivicNotice"
    assert data["status"] == "notice compliance foundation"
    assert "CivicCore-backed deadline plans" in data["message"]
    assert "local-first database-backed registry/deadline workpapers" in data["message"]
    assert "official publication" in data["message"]
    assert data["next_step"].startswith("Open /civicnotice/staff")


def test_health_endpoint_reports_versions() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "civicnotice"
    assert data["version"] == "0.1.2"
    assert data["civiccore_version"] == "1.2.0"


def test_readiness_is_green_with_default_local_database() -> None:
    response = client.get("/api/v1/civicnotice/readiness")
    assert response.status_code == 200
    data = response.json()

    assert data["ready"] is True
    assert data["schema_ready"] is True
    assert data["using_default_local_database"] is True
    assert data["workpaper_database_configured"] is True


def test_integration_contracts_advertise_suite_handoffs() -> None:
    response = client.get("/api/v1/civicnotice/integration-contracts")
    assert response.status_code == 200
    data = response.json()
    contracts = {contract["name"] for contract in data["contracts"]}

    assert "civicnotice.notice_registry.v1" in contracts
    assert "civicnotice.staff_review_queue.v1" in contracts
    assert "civicnotice.publication_packet.v1" in contracts
    assert "civicnotice.records_export.v1" in contracts
    assert "civicboards vacancy public notices" in data["downstream_ready_for"]
