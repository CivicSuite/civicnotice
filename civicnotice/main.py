"""FastAPI runtime foundation for CivicNotice."""

from datetime import date
import os

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from civicnotice import __version__
from civicnotice.accessibility_review import build_accessibility_review
from civicnotice.archive_packet import build_notice_archive_packet
from civicnotice.channel_plan import plan_notice_channels
from civicnotice.deadline_tracker import build_deadline_plan
from civicnotice.notice_templates import build_notice_template
from civicnotice.notice_registry import register_notice_stub
from civicnotice.persistence import (
    NoticeWorkpaperRepository,
    StoredDeadlinePlan,
    StoredNoticeRecord,
    StoredPublicationProof,
)
from civicnotice.public_ui import render_public_lookup_page
from civicnotice.publication_check import build_publication_checklist
from civicnotice.records_export import build_notice_records_export
from civicnotice.statutory_rules import check_statutory_notice_requirements
from civicnotice.subscriber_delivery import Subscriber, build_subscriber_delivery_plan


app = FastAPI(
    title="CivicNotice",
    version=__version__,
    description="Public hearing, legal notice, bid notice, vacancy notice, and statutory publication deadline support for CivicSuite.",
)

_workpaper_repository: NoticeWorkpaperRepository | None = None
_workpaper_db_url: str | None = None


class NoticeRegistryRequest(BaseModel):
    notice_id: str
    notice_type: str
    owner: str


class DeadlineRequest(BaseModel):
    notice_type: str
    event_date: date
    lead_days: int = 10


class PublicationRequest(BaseModel):
    notice_type: str
    channel: str


class RuleCheckRequest(BaseModel):
    notice_type: str
    event_date: date
    publication_dates: list[date] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    content_fields: list[str] = Field(default_factory=list)
    statutory_basis: str = ""


class NoticeTemplateRequest(BaseModel):
    notice_type: str
    matter_title: str
    event_date: date
    location: str = ""
    contact: str = ""
    source_module: str = "manual"
    statutory_basis: str = ""


class ChannelRequest(BaseModel):
    notice_type: str
    audience: str


class SubscriberRequest(BaseModel):
    subscriber_id: str
    name: str
    email: str = ""
    channels: list[str] = Field(default_factory=list)
    language: str = "English"
    active: bool = True


class SubscriberDeliveryRequest(BaseModel):
    notice_id: str
    notice_type: str
    audience: str
    subscribers: list[SubscriberRequest] = Field(default_factory=list)
    required_channels: list[str] = Field(default_factory=lambda: ["email"])


class AccessibilityReviewRequest(BaseModel):
    notice_id: str
    title: str
    notice_text: str
    target_languages: list[str] = Field(default_factory=list)
    attachments: list[str] = Field(default_factory=list)
    has_contact: bool = False
    has_event_date: bool = False
    has_plain_language_summary: bool = False


class ArchivePacketRequest(BaseModel):
    notice_id: str
    notice_type: str
    source_module: str = "manual"
    source_record_id: str = ""
    registry_record_id: str = ""
    deadline_plan_id: str = ""
    publication_proof_id: str = ""
    rule_check_complete: bool = False
    template_complete: bool = False
    accessibility_review_complete: bool = False
    subscriber_delivery_complete: bool = False
    records_export_complete: bool = False


class RecordsExportRequest(BaseModel):
    notice_id: str
    title: str
    format: str = "markdown"


class PublicationProofRequest(BaseModel):
    notice_id: str
    notice_type: str
    source_module: str = "manual"
    source_record_id: str
    channel: str
    published_at: str
    location: str
    confirmation_reference: str
    statutory_basis: str
    reviewer: str


@app.get("/")
def root() -> dict[str, str]:
    """Return current product state without overstating unshipped behavior."""

    return {
        "name": "CivicNotice",
        "version": __version__,
        "status": "notice compliance foundation",
        "message": (
            "CivicNotice package, API foundation, sample notice registry, CivicCore-backed deadline plans, "
            "statutory rule checks, notice drafting templates, accessibility and language-readiness packets, archive/handoff packets, publication-readiness checklist, channel planning, records export checklist, optional "
            "database-backed registry/deadline/publication-proof workpapers, and public UI foundation are online; official "
            "legal sufficiency decisions, official publication, legal "
            "advice, live LLM calls, publication-system write-back, and notice system-of-record integrations "
            "are not implemented yet."
        ),
        "next_step": "Post-v0.2.0 roadmap: jurisdiction-specific statutory rule packs, live CivicClerk/CivicProcure/CivicNotice handoffs, and publication proof queues",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Return dependency/version health for deployment smoke checks."""

    return {
        "status": "ok",
        "service": "civicnotice",
        "version": __version__,
        "civiccore_version": CIVICCORE_VERSION,
    }


@app.get("/civicnotice", response_class=HTMLResponse)
def public_civicnotice_page() -> str:
    """Return the public sample notice compliance support UI."""

    return render_public_lookup_page()


@app.post("/api/v1/civicnotice/registry")
def notice_registry(request: NoticeRegistryRequest) -> dict[str, object]:
    if _workpaper_database_url() is not None:
        return _stored_notice_response(
            _get_workpaper_repository().create_notice_record(
                notice_id=request.notice_id,
                notice_type=request.notice_type,
                owner=request.owner,
            )
        )
    payload = register_notice_stub(
        notice_id=request.notice_id,
        notice_type=request.notice_type,
        owner=request.owner,
    ).__dict__
    payload["record_id"] = None
    return payload


@app.get("/api/v1/civicnotice/registry/{record_id}")
def get_notice_registry(record_id: str) -> dict[str, object]:
    if _workpaper_database_url() is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "CivicNotice workpaper persistence is not configured.",
                "fix": "Set CIVICNOTICE_WORKPAPER_DB_URL to retrieve persisted notice registry records.",
            },
        )
    stored = _get_workpaper_repository().get_notice_record(record_id)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Notice registry record not found.",
                "fix": "Use a record_id returned by POST /api/v1/civicnotice/registry.",
            },
        )
    return _stored_notice_response(stored)


@app.post("/api/v1/civicnotice/deadlines")
def deadline_plan(request: DeadlineRequest) -> dict[str, object]:
    if _workpaper_database_url() is not None:
        return _stored_deadline_response(
            _get_workpaper_repository().create_deadline_plan(
                notice_type=request.notice_type,
                event_date=request.event_date,
                lead_days=request.lead_days,
            )
        )
    payload = build_deadline_plan(
        notice_type=request.notice_type,
        event_date=request.event_date,
        lead_days=request.lead_days,
    ).__dict__
    payload["plan_id"] = None
    return payload


@app.get("/api/v1/civicnotice/deadlines/{plan_id}")
def get_deadline_plan(plan_id: str) -> dict[str, object]:
    if _workpaper_database_url() is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "CivicNotice workpaper persistence is not configured.",
                "fix": "Set CIVICNOTICE_WORKPAPER_DB_URL to retrieve persisted deadline plans.",
            },
        )
    stored = _get_workpaper_repository().get_deadline_plan(plan_id)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Deadline plan record not found.",
                "fix": "Use a plan_id returned by POST /api/v1/civicnotice/deadlines.",
            },
        )
    return _stored_deadline_response(stored)


@app.post("/api/v1/civicnotice/publication-proof")
def publication_proof(request: PublicationProofRequest) -> dict[str, object]:
    if _workpaper_database_url() is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "CivicNotice workpaper persistence is not configured.",
                "fix": "Set CIVICNOTICE_WORKPAPER_DB_URL to store durable publication proof records.",
            },
        )
    stored = _get_workpaper_repository().create_publication_proof(
        notice_id=request.notice_id,
        notice_type=request.notice_type,
        source_module=request.source_module,
        source_record_id=request.source_record_id,
        channel=request.channel,
        published_at=request.published_at,
        location=request.location,
        confirmation_reference=request.confirmation_reference,
        statutory_basis=request.statutory_basis,
        reviewer=request.reviewer,
    )
    return _stored_publication_proof_response(stored)


@app.get("/api/v1/civicnotice/publication-proof/{proof_id}")
def get_publication_proof(proof_id: str) -> dict[str, object]:
    if _workpaper_database_url() is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "CivicNotice workpaper persistence is not configured.",
                "fix": "Set CIVICNOTICE_WORKPAPER_DB_URL to retrieve persisted publication proof records.",
            },
        )
    stored = _get_workpaper_repository().get_publication_proof(proof_id)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Publication proof record not found.",
                "fix": "Use a proof_id returned by POST /api/v1/civicnotice/publication-proof.",
            },
        )
    return _stored_publication_proof_response(stored)


@app.post("/api/v1/civicnotice/publication-check")
def publication_checklist(request: PublicationRequest) -> dict[str, object]:
    return build_publication_checklist(
        notice_type=request.notice_type,
        channel=request.channel,
    ).__dict__


@app.post("/api/v1/civicnotice/rule-check")
def rule_check(request: RuleCheckRequest) -> dict[str, object]:
    result = check_statutory_notice_requirements(
        notice_type=request.notice_type,
        event_date=request.event_date,
        publication_dates=tuple(request.publication_dates),
        channels=tuple(request.channels),
        content_fields=tuple(request.content_fields),
        statutory_basis=request.statutory_basis,
    )
    payload = result.__dict__.copy()
    payload["event_date"] = result.event_date.isoformat()
    payload["required_deadline_date"] = result.required_deadline_date.isoformat()
    payload["publication_dates"] = [value.isoformat() for value in result.publication_dates]
    return payload


@app.post("/api/v1/civicnotice/templates")
def notice_template(request: NoticeTemplateRequest) -> dict[str, object]:
    result = build_notice_template(
        notice_type=request.notice_type,
        matter_title=request.matter_title,
        event_date=request.event_date,
        location=request.location,
        contact=request.contact,
        source_module=request.source_module,
        statutory_basis=request.statutory_basis,
    )
    return result.__dict__


@app.post("/api/v1/civicnotice/channels")
def channel_plan(request: ChannelRequest) -> dict[str, object]:
    return plan_notice_channels(
        notice_type=request.notice_type,
        audience=request.audience,
    ).__dict__


@app.post("/api/v1/civicnotice/subscribers/plan")
def subscriber_delivery_plan(request: SubscriberDeliveryRequest) -> dict[str, object]:
    subscribers = tuple(
        Subscriber(
            subscriber_id=subscriber.subscriber_id,
            name=subscriber.name,
            email=subscriber.email,
            channels=tuple(subscriber.channels),
            language=subscriber.language,
            active=subscriber.active,
        )
        for subscriber in request.subscribers
    )
    return build_subscriber_delivery_plan(
        notice_id=request.notice_id,
        notice_type=request.notice_type,
        audience=request.audience,
        subscribers=subscribers,
        required_channels=tuple(request.required_channels),
    ).__dict__


@app.post("/api/v1/civicnotice/accessibility-review")
def accessibility_review(request: AccessibilityReviewRequest) -> dict[str, object]:
    return build_accessibility_review(
        notice_id=request.notice_id,
        title=request.title,
        notice_text=request.notice_text,
        target_languages=tuple(request.target_languages),
        attachments=tuple(request.attachments),
        has_contact=request.has_contact,
        has_event_date=request.has_event_date,
        has_plain_language_summary=request.has_plain_language_summary,
    ).__dict__


@app.post("/api/v1/civicnotice/archive-packet")
def archive_packet(request: ArchivePacketRequest) -> dict[str, object]:
    return build_notice_archive_packet(
        notice_id=request.notice_id,
        notice_type=request.notice_type,
        source_module=request.source_module,
        source_record_id=request.source_record_id,
        registry_record_id=request.registry_record_id,
        deadline_plan_id=request.deadline_plan_id,
        publication_proof_id=request.publication_proof_id,
        rule_check_complete=request.rule_check_complete,
        template_complete=request.template_complete,
        accessibility_review_complete=request.accessibility_review_complete,
        subscriber_delivery_complete=request.subscriber_delivery_complete,
        records_export_complete=request.records_export_complete,
    ).__dict__


@app.post("/api/v1/civicnotice/export")
def records_export(request: RecordsExportRequest) -> dict[str, object]:
    return build_notice_records_export(
        notice_id=request.notice_id,
        title=request.title,
        format=request.format,
    ).__dict__


def _workpaper_database_url() -> str | None:
    return os.environ.get("CIVICNOTICE_WORKPAPER_DB_URL")


def _get_workpaper_repository() -> NoticeWorkpaperRepository:
    global _workpaper_db_url, _workpaper_repository
    db_url = _workpaper_database_url()
    if db_url is None:
        raise RuntimeError("CIVICNOTICE_WORKPAPER_DB_URL is not configured.")
    if _workpaper_repository is None or db_url != _workpaper_db_url:
        _dispose_workpaper_repository()
        _workpaper_db_url = db_url
        _workpaper_repository = NoticeWorkpaperRepository(db_url=db_url)
    return _workpaper_repository


def _dispose_workpaper_repository() -> None:
    global _workpaper_repository
    if _workpaper_repository is not None:
        _workpaper_repository.engine.dispose()
        _workpaper_repository = None


def _stored_notice_response(stored: StoredNoticeRecord) -> dict[str, object]:
    return {
        "record_id": stored.record_id,
        "notice_id": stored.notice_id,
        "notice_type": stored.notice_type,
        "owner": stored.owner,
        "registry_notes": list(stored.registry_notes),
        "disclaimer": stored.disclaimer,
        "created_at": stored.created_at.isoformat(),
    }


def _stored_deadline_response(stored: StoredDeadlinePlan) -> dict[str, object]:
    return {
        "plan_id": stored.plan_id,
        "notice_type": stored.notice_type,
        "event_date": stored.event_date.isoformat(),
        "reminders": list(stored.reminders),
        "staff_review_required": stored.staff_review_required,
        "disclaimer": stored.disclaimer,
        "created_at": stored.created_at.isoformat(),
    }


def _stored_publication_proof_response(stored: StoredPublicationProof) -> dict[str, object]:
    return {
        "proof_id": stored.proof_id,
        "notice_id": stored.notice_id,
        "notice_type": stored.notice_type,
        "source_module": stored.source_module,
        "source_record_id": stored.source_record_id,
        "channel": stored.channel,
        "published_at": stored.published_at,
        "location": stored.location,
        "confirmation_reference": stored.confirmation_reference,
        "statutory_basis": stored.statutory_basis,
        "reviewer": stored.reviewer,
        "proof_notes": list(stored.proof_notes),
        "compliance_status": stored.compliance_status,
        "disclaimer": stored.disclaimer,
        "created_at": stored.created_at.isoformat(),
    }
