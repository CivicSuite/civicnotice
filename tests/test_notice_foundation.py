from datetime import date

from fastapi.testclient import TestClient

from civicnotice.accessibility_review import build_accessibility_review
from civicnotice.archive_packet import build_notice_archive_packet
from civicnotice.channel_plan import plan_notice_channels
from civicnotice.deadline_tracker import build_deadline_plan
from civicnotice.main import app
from civicnotice.notice_templates import build_notice_template
from civicnotice.notice_registry import register_notice_stub
from civicnotice.publication_check import build_publication_checklist
from civicnotice.records_export import build_notice_records_export
from civicnotice.statutory_rules import check_statutory_notice_requirements
from civicnotice.subscriber_delivery import Subscriber, build_subscriber_delivery_plan


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
    assert "official notice record" in result.disclaimer


def test_publication_checklist_requires_proof() -> None:
    result = build_publication_checklist(
        notice_type="vacancy notice",
        channel="newspaper",
    )
    assert result.proof_required is True
    assert "statutory citation" in result.checklist[0]
    assert "publication proof" in result.checklist[3]


def test_statutory_rule_check_flags_deadline_and_missing_requirements() -> None:
    result = check_statutory_notice_requirements(
        notice_type="planning hearing",
        event_date=date(2026, 6, 15),
        publication_dates=(date(2026, 6, 5),),
        channels=("city website",),
        content_fields=("title", "hearing date", "location"),
    )
    assert result.required_deadline_date == date(2026, 5, 31)
    assert result.deadline_status == "deadline_risk_staff_review_required"
    assert result.publication_count_status == "required_publication_count_met"
    assert result.missing_channels == ("posting board",)
    assert "case number" in result.missing_content
    assert result.staff_review_required is True


def test_notice_template_preserves_staff_review_placeholders() -> None:
    result = build_notice_template(
        notice_type="bid notice",
        matter_title="Water main replacement bid",
        event_date=date(2026, 7, 1),
        location="",
        contact="clerk@example.gov",
        source_module="civicprocure",
    )
    assert result.notice_type == "bid notice"
    assert result.source_module == "civicprocure"
    assert "submission location" in result.required_fields
    assert "[staff must enter location]" in result.placeholders_remaining
    assert "Staff must verify required publication channels" in result.template_lines[-1]


def test_notice_type_aliases_resolve_without_generic_downgrade() -> None:
    rule_check = check_statutory_notice_requirements(
        notice_type="public_hearing",
        event_date=date(2026, 8, 1),
        content_fields=("title", "hearing date", "location", "case number", "statutory basis"),
        channels=("city website", "posting board"),
        statutory_basis="staff-entered basis",
    )
    template = build_notice_template(
        notice_type="public-hearing",
        matter_title="Planning hearing",
        event_date=date(2026, 8, 1),
        location="Council Chambers",
        contact="clerk@example.gov",
    )
    assert rule_check.notice_type == "planning hearing"
    assert "case number" not in rule_check.missing_content
    assert rule_check.staff_review_required is True
    assert template.notice_type == "planning hearing"
    assert "case number" in template.required_fields


def test_unknown_notice_type_is_rejected_with_supported_choices() -> None:
    response = client.post(
        "/api/v1/civicnotice/rule-check",
        json={
            "notice_type": "river festival notice",
            "event_date": "2026-08-01",
            "content_fields": ["title"],
        },
    )
    template = client.post(
        "/api/v1/civicnotice/templates",
        json={
            "notice_type": "river festival notice",
            "matter_title": "River festival street closure",
            "event_date": "2026-08-01",
            "location": "Main Street",
            "contact": "clerk@example.gov",
        },
    )
    assert response.status_code == 422
    assert template.status_code == 422
    assert "Supported notice types" in response.json()["detail"]["message"]
    assert "planning hearing" in response.json()["detail"]["supported_notice_types"]


def test_channel_plan_flags_accessibility_review() -> None:
    result = plan_notice_channels(
        notice_type="public hearing",
        audience="residents near the project site",
    )
    assert result.staff_review_required is True
    assert "newspaper or legal publication if required" in result.channels
    assert any("ADA format" in note for note in result.accessibility_notes)


def test_subscriber_delivery_plan_dedupes_and_flags_review() -> None:
    result = build_subscriber_delivery_plan(
        notice_id="hear-001",
        notice_type="planning hearing",
        audience="planning subscribers",
        subscribers=(
            Subscriber(
                subscriber_id="1",
                name="Alex Resident",
                email="alex@example.gov",
                channels=("Email",),
                language="English",
            ),
            Subscriber(
                subscriber_id="2",
                name="Alex Duplicate",
                email="ALEX@example.gov",
                channels=("email",),
                language="Spanish",
            ),
            Subscriber(
                subscriber_id="3",
                name="Inactive Resident",
                email="inactive@example.gov",
                channels=("email",),
                language="English",
                active=False,
            ),
        ),
        required_channels=("email", "postal mail"),
    )
    assert result.active_subscriber_count == 2
    assert result.suppressed_subscriber_count == 1
    assert result.email_recipients == ("alex@example.gov",)
    assert result.missing_required_channels == ("postal mail",)
    assert result.language_review_required is True
    assert result.staff_review_required is True


def test_accessibility_review_flags_language_and_plain_language_needs() -> None:
    result = build_accessibility_review(
        notice_id="hear-001",
        title="Planning hearing",
        notice_text="Pursuant to the aforementioned provisions, the city hereby notices a hearing.",
        target_languages=("English", "Spanish"),
        attachments=("notice.pdf",),
        has_contact=False,
        has_event_date=True,
        has_plain_language_summary=False,
    )
    assert "public contact for accommodations or questions" in result.missing_accessibility_items
    assert "plain-language summary for public readers" in result.missing_accessibility_items
    assert "legal or technical jargon review" in result.plain_language_flags
    assert result.translation_tasks == (
        "Prepare human-approved Spanish notice version or language-access note.",
    )
    assert result.attachment_review_required is True
    assert result.staff_review_required is True


def test_archive_packet_tracks_missing_and_complete_evidence() -> None:
    incomplete = build_notice_archive_packet(
        notice_id="hear-001",
        notice_type="planning hearing",
        source_module="civicclerk",
        source_record_id="meeting-42",
        registry_record_id="registry-1",
        deadline_plan_id="deadline-1",
    )
    complete = build_notice_archive_packet(
        notice_id="hear-001",
        notice_type="planning hearing",
        source_module="civicclerk",
        source_record_id="meeting-42",
        registry_record_id="registry-1",
        deadline_plan_id="deadline-1",
        publication_proof_id="proof-1",
        rule_check_complete=True,
        template_complete=True,
        accessibility_review_complete=True,
        subscriber_delivery_complete=True,
        records_export_complete=True,
    )
    assert incomplete.readiness_status == "archive_packet_incomplete_staff_review_required"
    assert "publication proof" in incomplete.missing_items
    assert complete.readiness_status == "archive_packet_ready_for_staff_final_review"
    assert complete.missing_items == ()
    assert complete.handoff_targets == ("civicclerk", "civicrecords")


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
    rule_check = client.post(
        "/api/v1/civicnotice/rule-check",
        json={
            "notice_type": "planning hearing",
            "event_date": "2026-06-15",
            "publication_dates": ["2026-05-30"],
            "channels": ["city website", "posting board"],
            "content_fields": [
                "title",
                "hearing date",
                "location",
                "case number",
                "statutory basis",
            ],
            "statutory_basis": "staff-entered basis",
        },
    )
    template = client.post(
        "/api/v1/civicnotice/templates",
        json={
            "notice_type": "planning hearing",
            "matter_title": "Planning hearing",
            "event_date": "2026-06-15",
            "location": "Council Chambers",
            "contact": "clerk@example.gov",
            "source_module": "civicclerk",
            "statutory_basis": "staff-entered basis",
        },
    )
    channels = client.post(
        "/api/v1/civicnotice/channels",
        json={"notice_type": "public hearing", "audience": "residents"},
    )
    subscribers = client.post(
        "/api/v1/civicnotice/subscribers/plan",
        json={
            "notice_id": "hear-001",
            "notice_type": "public hearing",
            "audience": "residents",
            "subscribers": [
                {
                    "subscriber_id": "1",
                    "name": "Alex Resident",
                    "email": "alex@example.gov",
                    "channels": ["email"],
                    "language": "English",
                    "active": True,
                }
            ],
            "required_channels": ["email"],
        },
    )
    accessibility = client.post(
        "/api/v1/civicnotice/accessibility-review",
        json={
            "notice_id": "hear-001",
            "title": "Planning hearing",
            "notice_text": "Pursuant to the applicable provisions, a hearing is scheduled.",
            "target_languages": ["Spanish"],
            "attachments": ["notice.pdf"],
            "has_contact": True,
            "has_event_date": True,
            "has_plain_language_summary": False,
        },
    )
    archive = client.post(
        "/api/v1/civicnotice/archive-packet",
        json={
            "notice_id": "hear-001",
            "notice_type": "public hearing",
            "source_module": "civicclerk",
            "source_record_id": "meeting-42",
            "registry_record_id": "registry-1",
            "deadline_plan_id": "deadline-1",
            "publication_proof_id": "proof-1",
            "rule_check_complete": True,
            "template_complete": True,
            "accessibility_review_complete": True,
            "subscriber_delivery_complete": True,
            "records_export_complete": True,
        },
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
    assert rule_check.status_code == 200
    assert rule_check.json()["deadline_status"] == "meets_minimum_lead_time"
    assert rule_check.json()["missing_channels"] == []
    assert template.status_code == 200
    assert template.json()["source_module"] == "civicclerk"
    assert template.json()["staff_review_required"] is True
    assert channels.status_code == 200
    assert channels.json()["staff_review_required"] is True
    assert subscribers.status_code == 200
    assert subscribers.json()["email_recipients"] == ["alex@example.gov"]
    assert subscribers.json()["missing_required_channels"] == []
    assert accessibility.status_code == 200
    assert accessibility.json()["translation_tasks"] == [
        "Prepare human-approved Spanish notice version or language-access note."
    ]
    assert accessibility.json()["staff_review_required"] is True
    assert archive.status_code == 200
    assert archive.json()["readiness_status"] == "archive_packet_ready_for_staff_final_review"
    assert archive.json()["handoff_targets"] == ["civicclerk", "civicrecords"]
    assert export.status_code == 200
    assert export.json()["notice_id"] == "hear-001"


def test_public_ui_route_is_accessible_and_honest() -> None:
    response = client.get("/civicnotice")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    text = response.text
    assert '<a class="skip-link" href="#main">Skip to main content</a>' in text
    assert '<main id="main" tabindex="-1">' in text
    assert "<button" not in text
    assert "<textarea" not in text
    assert 'class="sample-box"' in text
    assert 'href="/docs"' in text
    assert 'href="/openapi.json"' in text
    assert "Supported rule-check and template notice types include planning hearing" in text
    assert "v0.2.0 notice compliance foundation" in text
    assert "does not determine legal sufficiency" in text
    assert "replace the notice system of record" in text
