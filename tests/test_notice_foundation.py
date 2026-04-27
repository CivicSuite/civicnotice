from datetime import date

from fastapi.testclient import TestClient

from civicnotice.channel_plan import plan_notice_channels
from civicnotice.deadline_tracker import build_deadline_plan
from civicnotice.main import app
from civicnotice.notice_registry import register_notice_stub
from civicnotice.publication_check import build_publication_checklist
from civicnotice.records_export import build_notice_records_export


client = TestClient(app)


def test_notice_registry_flags_authority_and_boundary() -> None:
    result = register_notice_stub(
        notice_id="hear-001",
        notice_type="public hearing",
        owner="clerk@example.gov",
    )
    assert result.notice_id == "hear-001"
    assert result.notice_type == "public hearing"
    assert any("statutory authority" in note for note in result.registry_notes)
    assert "legal sufficiency" in result.disclaimer


def test_deadline_plan_builds_publication_reminders() -> None:
    result = build_deadline_plan(
        notice_type="bid notice",
        event_date=date(2026, 6, 15),
        lead_days=14,
    )
    assert result.notice_type == "bid notice"
    assert len(result.reminders) == 4
    assert "publish or file proof" in result.reminders[2]
    assert result.staff_review_required is True


def test_publication_checklist_requires_proof() -> None:
    result = build_publication_checklist(
        notice_type="vacancy notice",
        channel="newspaper",
    )
    assert result.proof_required is True
    assert "statutory citation" in result.checklist[0]
    assert "publication proof" in result.checklist[3]


def test_channel_plan_flags_accessibility_review() -> None:
    result = plan_notice_channels(
        notice_type="public hearing",
        audience="residents near the project site",
    )
    assert result.staff_review_required is True
    assert "newspaper or legal publication if required" in result.channels
    assert any("ADA format" in note for note in result.accessibility_notes)


def test_records_export_preserves_notice_context() -> None:
    result = build_notice_records_export(
        notice_id="hear-001",
        title="Planning hearing notice archive",
    )
    assert result.notice_id == "hear-001"
    assert "publication proof" in result.checklist[0]
    assert "retention schedule" in result.retention_note


def test_notice_support_apis_success_shape() -> None:
    registry = client.post(
        "/api/v1/civicnotice/registry",
        json={
            "notice_id": "hear-001",
            "notice_type": "public hearing",
            "owner": "clerk@example.gov",
        },
    )
    deadlines = client.post(
        "/api/v1/civicnotice/deadlines",
        json={"notice_type": "bid notice", "event_date": "2026-06-15", "lead_days": 14},
    )
    publication = client.post(
        "/api/v1/civicnotice/publication-check",
        json={"notice_type": "vacancy notice", "channel": "newspaper"},
    )
    channels = client.post(
        "/api/v1/civicnotice/channels",
        json={"notice_type": "public hearing", "audience": "residents"},
    )
    export = client.post(
        "/api/v1/civicnotice/export",
        json={"title": "Planning hearing notice archive", "notice_id": "hear-001"},
    )
    assert registry.status_code == 200
    assert registry.json()["notice_id"] == "hear-001"
    assert deadlines.status_code == 200
    assert len(deadlines.json()["reminders"]) == 4
    assert publication.status_code == 200
    assert publication.json()["proof_required"] is True
    assert channels.status_code == 200
    assert channels.json()["staff_review_required"] is True
    assert export.status_code == 200
    assert export.json()["notice_id"] == "hear-001"


def test_public_ui_route_is_accessible_and_honest() -> None:
    response = client.get("/civicnotice")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    text = response.text
    assert '<a class="skip-link" href="#main">Skip to main content</a>' in text
    assert '<main id="main" tabindex="-1">' in text
    assert "v0.1.0 notice compliance foundation" in text
    assert "does not determine legal sufficiency" in text
    assert "replace the notice system of record" in text
