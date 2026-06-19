from datetime import date, timedelta

from fastapi.testclient import TestClient

from civicnotice.archive_packet import build_notice_archive_packet
from civicnotice.main import app
from civicnotice.publication_proof import record_publication_proof
from civicnotice.statutory_rules import RULE_PACKS, check_statutory_notice_requirements
from civicnotice.subscriber_delivery import Subscriber, build_subscriber_delivery_plan


client = TestClient(app)


def test_openapi_documents_persistence_failure_contracts() -> None:
    openapi = client.get("/openapi.json").json()
    paths = openapi["paths"]
    persistence_gets = [
        ("/api/v1/civicnotice/registry/{record_id}", "get"),
        ("/api/v1/civicnotice/deadlines/{plan_id}", "get"),
        ("/api/v1/civicnotice/publication-proof/{proof_id}", "get"),
    ]
    persistence_writes = [
        ("/api/v1/civicnotice/registry", "post"),
        ("/api/v1/civicnotice/deadlines", "post"),
        ("/api/v1/civicnotice/publication-proof", "post"),
    ]
    for path, method in persistence_gets:
        responses = paths[path][method]["responses"]
        assert "404" in responses
        assert "503" in responses
    for path, method in persistence_writes:
        responses = paths[path][method]["responses"]
        assert "403" in responses
        assert "503" in responses


def test_api_rejects_fields_longer_than_storage_contract() -> None:
    too_long = "x" * 161
    response = client.post(
        "/api/v1/civicnotice/registry",
        json={"notice_id": too_long, "notice_type": "hearing", "owner": "Clerk"},
    )
    assert response.status_code == 422


def test_all_rule_packs_return_serializable_deadline_checks() -> None:
    for notice_type, rule in RULE_PACKS.items():
        event_date = date(2026, 7, 1)
        publication_date = event_date - timedelta(days=rule.minimum_lead_days)
        result = check_statutory_notice_requirements(
            notice_type=notice_type,
            event_date=event_date,
            publication_dates=(publication_date,),
            channels=rule.required_channels,
            content_fields=rule.required_content,
            statutory_basis="staff-entered basis",
        )
        assert result.notice_type == notice_type
        assert result.publication_count_status == "required_publication_count_met"
        assert result.missing_channels == ()
        assert result.missing_content == ()


def test_publication_proof_fallbacks_are_staff_reviewable() -> None:
    result = record_publication_proof(
        notice_id="",
        notice_type="",
        source_module="",
        source_record_id="",
        channel="",
        published_at="",
        location="",
        confirmation_reference="",
        statutory_basis="",
        reviewer="",
    )
    assert result.notice_id == "unassigned notice"
    assert result.source_record_id == "unlinked source record"
    assert result.confirmation_reference == "pending confirmation reference"
    assert result.compliance_status == "proof_recorded_staff_review_required"


def test_archive_packet_handoff_targets_cover_source_modules() -> None:
    expected = {
        "civicclerk": ("civicclerk", "civicrecords"),
        "civicprocure": ("civicprocure", "civicrecords"),
        "civicboards": ("civicboards", "civicrecords"),
        "manual": ("manual staff archive", "civicrecords"),
    }
    for source_module, targets in expected.items():
        result = build_notice_archive_packet(
            notice_id="N-1",
            notice_type="hearing",
            source_module=source_module,
            source_record_id="source-1",
        )
        assert result.handoff_targets == targets


def test_subscriber_delivery_empty_and_required_channel_variants() -> None:
    empty = build_subscriber_delivery_plan(
        notice_id="N-1",
        notice_type="hearing",
        audience="residents",
        subscribers=(),
        required_channels=("email",),
    )
    postal = build_subscriber_delivery_plan(
        notice_id="N-1",
        notice_type="hearing",
        audience="residents",
        subscribers=(
            Subscriber(
                subscriber_id="1",
                name="Resident",
                email="resident@example.gov",
                channels=("postal mail",),
                language="English",
            ),
        ),
        required_channels=("postal mail",),
    )
    assert empty.active_subscriber_count == 0
    assert empty.missing_required_channels == ("email",)
    assert postal.missing_required_channels == ()
    assert postal.email_recipients == ()
