from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from civicnotice.main import app, _dispose_workpaper_repository
from civicnotice.persistence import NoticeWorkpaperRepository


client = TestClient(app)


def test_repository_persists_registry_and_deadline(tmp_path: Path) -> None:
    db_path = tmp_path / "civicnotice.db"
    db_url = f"sqlite+pysqlite:///{db_path.as_posix()}"
    repository = NoticeWorkpaperRepository(db_url=db_url)
    record = repository.create_notice_record(notice_id="N-1", notice_type="hearing", owner="Clerk")
    plan = repository.create_deadline_plan(notice_type="hearing", event_date=date(2026, 5, 20))
    proof = repository.create_publication_proof(
        notice_id="N-1",
        notice_type="hearing",
        source_module="civicclerk",
        source_record_id="meeting-42",
        channel="newspaper",
        published_at="2026-05-10T09:00:00-06:00",
        location="Daily Gazette",
        confirmation_reference="DG-12345",
        statutory_basis="MCA hearing notice",
        reviewer="Deputy Clerk",
    )
    repository.engine.dispose()
    reloaded = NoticeWorkpaperRepository(db_url=db_url)
    assert reloaded.get_notice_record(record.record_id).owner == "Clerk"
    stored_plan = reloaded.get_deadline_plan(plan.plan_id)
    stored_proof = reloaded.get_publication_proof(proof.proof_id)
    assert stored_plan.staff_review_required is True
    assert "official notice record" in stored_plan.disclaimer
    assert stored_proof.source_module == "civicclerk"
    assert stored_proof.source_record_id == "meeting-42"
    assert stored_proof.confirmation_reference == "DG-12345"
    assert stored_proof.compliance_status == "proof_recorded_staff_review_required"
    reloaded.engine.dispose()
    db_path.unlink()


def test_notice_persistence_api_round_trip(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicnotice-api.db"
    monkeypatch.setenv("CIVICNOTICE_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    _dispose_workpaper_repository()
    created_record = client.post(
        "/api/v1/civicnotice/registry",
        json={"notice_id": "N-1", "notice_type": "hearing", "owner": "Clerk"},
    )
    record_id = created_record.json()["record_id"]
    fetched_record = client.get(f"/api/v1/civicnotice/registry/{record_id}")
    created_plan = client.post(
        "/api/v1/civicnotice/deadlines",
        json={"notice_type": "hearing", "event_date": "2026-05-20", "lead_days": 10},
    )
    plan_id = created_plan.json()["plan_id"]
    fetched_plan = client.get(f"/api/v1/civicnotice/deadlines/{plan_id}")
    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICNOTICE_WORKPAPER_DB_URL")
    assert fetched_record.status_code == 200
    assert fetched_record.json()["notice_id"] == "N-1"
    assert fetched_plan.status_code == 200
    assert fetched_plan.json()["staff_review_required"] is True
    assert "official notice record" in fetched_plan.json()["disclaimer"]
    db_path.unlink()


def test_publication_proof_api_round_trip(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicnotice-proof.db"
    monkeypatch.setenv("CIVICNOTICE_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    _dispose_workpaper_repository()
    created_proof = client.post(
        "/api/v1/civicnotice/publication-proof",
        json={
            "notice_id": "N-2",
            "notice_type": "hearing",
            "source_module": "civicclerk",
            "source_record_id": "meeting-99",
            "channel": "public website",
            "published_at": "2026-05-10T09:00:00-06:00",
            "location": "city.example.gov/notices/N-2",
            "confirmation_reference": "CMS-98765",
            "statutory_basis": "staff-entered hearing notice basis",
            "reviewer": "City Clerk",
        },
    )
    proof_id = created_proof.json()["proof_id"]
    fetched_proof = client.get(f"/api/v1/civicnotice/publication-proof/{proof_id}")
    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICNOTICE_WORKPAPER_DB_URL")
    assert fetched_proof.status_code == 200
    payload = fetched_proof.json()
    assert payload["notice_id"] == "N-2"
    assert payload["source_module"] == "civicclerk"
    assert payload["source_record_id"] == "meeting-99"
    assert payload["confirmation_reference"] == "CMS-98765"
    assert "does not certify legal sufficiency" in " ".join(payload["proof_notes"])
    db_path.unlink()


def test_get_registry_without_persistence_returns_actionable_503(monkeypatch) -> None:
    monkeypatch.delenv("CIVICNOTICE_WORKPAPER_DB_URL", raising=False)
    _dispose_workpaper_repository()
    response = client.get("/api/v1/civicnotice/registry/example")
    assert response.status_code == 503
    assert "Set CIVICNOTICE_WORKPAPER_DB_URL" in response.json()["detail"]["fix"]


def test_get_deadline_missing_id_returns_actionable_404(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicnotice-missing.db"
    monkeypatch.setenv("CIVICNOTICE_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    _dispose_workpaper_repository()
    response = client.get("/api/v1/civicnotice/deadlines/missing")
    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICNOTICE_WORKPAPER_DB_URL")
    assert response.status_code == 404
    assert "POST /api/v1/civicnotice/deadlines" in response.json()["detail"]["fix"]
    db_path.unlink()


def test_publication_proof_without_persistence_returns_actionable_503(monkeypatch) -> None:
    monkeypatch.delenv("CIVICNOTICE_WORKPAPER_DB_URL", raising=False)
    _dispose_workpaper_repository()
    response = client.post(
        "/api/v1/civicnotice/publication-proof",
        json={
            "notice_id": "N-3",
            "notice_type": "hearing",
            "source_record_id": "meeting-100",
            "channel": "newspaper",
            "published_at": "2026-05-10",
            "location": "Daily Gazette",
            "confirmation_reference": "DG-333",
            "statutory_basis": "staff-entered basis",
            "reviewer": "City Clerk",
        },
    )
    assert response.status_code == 503
    assert "Set CIVICNOTICE_WORKPAPER_DB_URL" in response.json()["detail"]["fix"]
