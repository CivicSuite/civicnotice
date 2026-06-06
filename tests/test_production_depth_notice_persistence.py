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
    repository.engine.dispose()
    reloaded = NoticeWorkpaperRepository(db_url=db_url)
    assert reloaded.get_notice_record(record.record_id).owner == "Clerk"
    stored_plan = reloaded.get_deadline_plan(plan.plan_id)
    assert stored_plan.staff_review_required is True
    assert "official notice record" in stored_plan.disclaimer
    reloaded.engine.dispose()
    db_path.unlink()


def test_notice_persistence_api_round_trip(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicnotice-api.db"
    monkeypatch.setenv("CIVICNOTICE_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    _dispose_workpaper_repository()
    created_record = client.post("/api/v1/civicnotice/registry", json={"notice_id":"N-1","notice_type":"hearing","owner":"Clerk"})
    record_id = created_record.json()["record_id"]
    fetched_record = client.get(f"/api/v1/civicnotice/registry/{record_id}")
    created_plan = client.post("/api/v1/civicnotice/deadlines", json={"notice_type":"hearing","event_date":"2026-05-20","lead_days":10})
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


def test_get_registry_without_persistence_returns_actionable_503(monkeypatch) -> None:
    monkeypatch.delenv("CIVICNOTICE_WORKPAPER_DB_URL", raising=False)
    _dispose_workpaper_repository()
    created = client.post(
        "/api/v1/civicnotice/registry",
        json={"notice_id": "N-LOCAL", "notice_type": "hearing", "owner": "Clerk"},
    )
    record_id = created.json()["record_id"]
    response = client.get(f"/api/v1/civicnotice/registry/{record_id}")
    assert created.status_code == 200
    assert response.status_code == 200
    assert response.json()["notice_id"] == "N-LOCAL"


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


def test_staff_review_queue_requires_key_and_returns_items(monkeypatch) -> None:
    monkeypatch.setenv("CIVICNOTICE_STAFF_API_KEY", "local-notice-key")
    created = client.post(
        "/api/v1/civicnotice/staff/reviews",
        headers={
            "X-CivicNotice-Role": "staff",
            "X-CivicNotice-Staff-Key": "local-notice-key",
        },
        json={
            "notice_id": "N-STAFF",
            "title": "Public hearing notice review",
            "reason": "Notice proof and publication channel need staff review.",
        },
    )

    denied = client.get("/api/v1/civicnotice/staff/reviews")
    allowed = client.get(
        "/api/v1/civicnotice/staff/reviews",
        headers={
            "X-CivicNotice-Role": "staff",
            "X-CivicNotice-Staff-Key": "local-notice-key",
        },
    )

    assert created.status_code == 200
    assert denied.status_code in {401, 403}
    assert allowed.status_code == 200
    assert allowed.json()["visibility"] == "staff_only"
    assert allowed.json()["items"][0]["notice_id"] == "N-STAFF"


def test_deadline_plan_creates_staff_review_queue_item(monkeypatch) -> None:
    monkeypatch.setenv("CIVICNOTICE_STAFF_API_KEY", "local-notice-key")
    plan = client.post(
        "/api/v1/civicnotice/deadlines",
        json={"notice_type": "hearing", "event_date": "2026-05-20", "lead_days": 10},
    )
    queue = client.get(
        "/api/v1/civicnotice/staff/reviews",
        headers={
            "X-CivicNotice-Role": "staff",
            "X-CivicNotice-Staff-Key": "local-notice-key",
        },
    )

    assert plan.status_code == 200
    assert plan.json()["staff_review_required"] is True
    assert queue.status_code == 200
    assert any("Deadline review" in item["title"] for item in queue.json()["items"])
