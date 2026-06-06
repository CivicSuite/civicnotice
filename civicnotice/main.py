"""FastAPI runtime foundation for CivicNotice."""

from datetime import date
import os
from pathlib import Path

from civiccore import __version__ as CIVICCORE_VERSION
from civiccore.auth import staff_key_gate
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from civicnotice import __version__
from civicnotice.channel_plan import plan_notice_channels
from civicnotice.persistence import (
    NoticeWorkpaperRepository,
    StaffReviewQueueItem,
    StoredDeadlinePlan,
    StoredNoticeRecord,
)
from civicnotice.public_ui import render_public_lookup_page, render_staff_page
from civicnotice.publication_check import build_publication_checklist
from civicnotice.records_export import build_notice_records_export


app = FastAPI(
    title="CivicNotice",
    version=__version__,
    description="Public hearing, legal notice, bid notice, vacancy notice, and statutory publication deadline support for CivicSuite.",
)

_workpaper_repository: NoticeWorkpaperRepository | None = None
_workpaper_db_url: str | None = None
_require_staff_key = staff_key_gate("CIVICNOTICE_STAFF_API_KEY", "X-CivicNotice-Staff-Key")


class NoticeRegistryRequest(BaseModel):
    notice_id: str = Field(..., min_length=1, max_length=160)
    notice_type: str = Field(..., min_length=1, max_length=160)
    owner: str = Field(..., min_length=1, max_length=160)


class DeadlineRequest(BaseModel):
    notice_type: str
    event_date: date
    lead_days: int = 10


class PublicationRequest(BaseModel):
    notice_type: str
    channel: str


class ChannelRequest(BaseModel):
    notice_type: str
    audience: str


class RecordsExportRequest(BaseModel):
    notice_id: str
    title: str
    format: str = "markdown"


class StaffReviewCreateRequest(BaseModel):
    notice_id: str = Field(..., min_length=1, max_length=160)
    title: str = Field(..., min_length=1, max_length=500)
    reason: str = Field(..., min_length=1, max_length=1000)


@app.get("/")
def root() -> dict[str, str]:
    """Return current product state without overstating unshipped behavior."""

    return {
        "name": "CivicNotice",
        "version": __version__,
        "status": "notice compliance foundation",
        "message": (
            "CivicNotice package, API foundation, sample notice registry, CivicCore-backed deadline plans, "
            "publication-readiness checklist, channel planning, records export checklist, local-first "
            "database-backed registry/deadline workpapers, staff review queues, suite handoff contracts, "
            "and public/staff UI foundations are online; official "
            "legal sufficiency decisions, official publication, legal "
            "advice, live LLM calls, publication-system write-back, and notice system-of-record integrations "
            "are not implemented."
        ),
        "next_step": "Open /civicnotice/staff for notice registry intake, deadline review, and staff queue triage.",
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


@app.get("/ready")
def ready() -> dict[str, object]:
    return _readiness_payload()


@app.get("/api/v1/civicnotice/readiness")
def readiness() -> dict[str, object]:
    return _readiness_payload()


@app.get("/civicnotice", response_class=HTMLResponse)
def public_civicnotice_page() -> str:
    """Return the public sample notice compliance support UI."""

    return render_public_lookup_page()


@app.get("/civicnotice/staff", response_class=HTMLResponse)
def staff_civicnotice_page() -> str:
    """Return the staff notice review queue UI."""

    return render_staff_page()


@app.get("/api/v1/civicnotice/integration-contracts")
def integration_contracts() -> dict[str, object]:
    """Return suite-visible integration contracts for installer and downstream checks."""

    return {
        "module": "civicnotice",
        "version": __version__,
        "contracts": [
            {
                "name": "civicnotice.notice_registry.v1",
                "endpoint": "/api/v1/civicnotice/registry",
                "method": "POST",
                "boundary": "Creates notice registry records; it does not publish official notices.",
            },
            {
                "name": "civicnotice.staff_review_queue.v1",
                "endpoint": "/api/v1/civicnotice/staff/reviews",
                "method": "GET",
                "requires_staff_key": True,
                "boundary": "Staff-only queue for notice, deadline, proof, and channel review.",
            },
            {
                "name": "civicnotice.publication_packet.v1",
                "endpoint": "/api/v1/civicnotice/publication-check",
                "method": "POST",
                "boundary": "Builds publication checklists; it does not determine legal sufficiency.",
            },
            {
                "name": "civicnotice.records_export.v1",
                "endpoint": "/api/v1/civicnotice/export",
                "method": "POST",
                "boundary": "Builds notice records export checklists; it does not publish or redact records.",
            },
        ],
        "downstream_ready_for": [
            "civicclerk agenda public notices",
            "civicboards vacancy public notices",
            "civicprocure bid notices",
            "civicrecords-ai notice file retention",
            "civiclegal legal sufficiency review",
        ],
    }


@app.post("/api/v1/civicnotice/registry")
def notice_registry(request: NoticeRegistryRequest) -> dict[str, object]:
    return _stored_notice_response(_get_workpaper_repository().create_notice_record(
            notice_id=request.notice_id,
            notice_type=request.notice_type,
            owner=request.owner,
    ))

@app.get("/api/v1/civicnotice/registry/{record_id}")
def get_notice_registry(record_id: str) -> dict[str, object]:
    stored = _get_workpaper_repository().get_notice_record(record_id)
    if stored is None:
        raise HTTPException(status_code=404, detail={"message":"Notice registry record not found.","fix":"Use a record_id returned by POST /api/v1/civicnotice/registry."})
    return _stored_notice_response(stored)


@app.post("/api/v1/civicnotice/deadlines")
def deadline_plan(request: DeadlineRequest) -> dict[str, object]:
    return _stored_deadline_response(_get_workpaper_repository().create_deadline_plan(
            notice_type=request.notice_type,
            event_date=request.event_date,
            lead_days=request.lead_days,
    ))

@app.get("/api/v1/civicnotice/deadlines/{plan_id}")
def get_deadline_plan(plan_id: str) -> dict[str, object]:
    stored = _get_workpaper_repository().get_deadline_plan(plan_id)
    if stored is None:
        raise HTTPException(status_code=404, detail={"message":"Deadline plan record not found.","fix":"Use a plan_id returned by POST /api/v1/civicnotice/deadlines."})
    return _stored_deadline_response(stored)


@app.post("/api/v1/civicnotice/publication-check")
def publication_checklist(request: PublicationRequest) -> dict[str, object]:
    return build_publication_checklist(
        notice_type=request.notice_type,
        channel=request.channel,
    ).__dict__


@app.post("/api/v1/civicnotice/channels")
def channel_plan(request: ChannelRequest) -> dict[str, object]:
    return plan_notice_channels(
        notice_type=request.notice_type,
        audience=request.audience,
    ).__dict__


@app.post("/api/v1/civicnotice/export")
def records_export(request: RecordsExportRequest) -> dict[str, object]:
    return build_notice_records_export(
        notice_id=request.notice_id,
        title=request.title,
        format=request.format,
    ).__dict__


@app.post("/api/v1/civicnotice/staff/reviews")
def create_staff_review(
    request: StaffReviewCreateRequest,
    _staff_principal: object = Depends(_require_staff_key),
) -> dict[str, object]:
    item = _get_workpaper_repository().create_staff_review_queue_item(
        notice_id=request.notice_id,
        title=request.title,
        reason=request.reason,
        created_by="staff",
    )
    return _staff_review_payload(item)


@app.get("/api/v1/civicnotice/staff/reviews")
def list_staff_reviews(
    status: str | None = None,
    _staff_principal: object = Depends(_require_staff_key),
) -> dict[str, object]:
    return {
        "visibility": "staff_only",
        "items": [
            _staff_review_payload(item)
            for item in _get_workpaper_repository().list_staff_review_queue_items(status=status)
        ],
    }


def _workpaper_database_url() -> str:
    configured = os.environ.get("CIVICNOTICE_WORKPAPER_DB_URL")
    if configured:
        return configured
    data_dir = Path(os.environ.get("CIVICNOTICE_DATA_DIR", Path.cwd() / "data")).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite+pysqlite:///{(data_dir / 'civicnotice-workpapers.db').as_posix()}"


def _uses_default_workpaper_database() -> bool:
    return not os.environ.get("CIVICNOTICE_WORKPAPER_DB_URL")

def _get_workpaper_repository() -> NoticeWorkpaperRepository:
    global _workpaper_db_url, _workpaper_repository
    db_url = _workpaper_database_url()
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
    return {"record_id": stored.record_id, "notice_id": stored.notice_id, "notice_type": stored.notice_type, "owner": stored.owner, "registry_notes": list(stored.registry_notes), "disclaimer": stored.disclaimer, "created_at": stored.created_at.isoformat()}

def _stored_deadline_response(stored: StoredDeadlinePlan) -> dict[str, object]:
    return {"plan_id": stored.plan_id, "notice_type": stored.notice_type, "event_date": stored.event_date.isoformat(), "reminders": list(stored.reminders), "staff_review_required": stored.staff_review_required, "disclaimer": stored.disclaimer, "created_at": stored.created_at.isoformat()}


def _staff_review_payload(item: StaffReviewQueueItem) -> dict[str, object]:
    return {
        "review_id": item.review_id,
        "notice_id": item.notice_id,
        "title": item.title,
        "reason": item.reason,
        "status": item.status,
        "assigned_to": item.assigned_to,
        "resolution": item.resolution,
        "created_by": item.created_by,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
        "visibility": "staff_only",
        "boundary": (
            "Staff review queues support notice administration only; they do not publish notices, "
            "determine legal sufficiency, or replace the notice system of record."
        ),
    }


def _readiness_payload() -> dict[str, object]:
    db_url = _workpaper_database_url()
    repository = _get_workpaper_repository()
    schema_status = repository.schema_status()
    blockers: list[str] = []
    if not schema_status.ready:
        blockers.append("Initialize the CivicNotice local workpaper database schema.")
    ready_for_public_use = not blockers
    return {
        "status": "ready" if ready_for_public_use else "not-ready",
        "ready": ready_for_public_use,
        "workpaper_database_configured": True,
        "workpaper_database_url": db_url,
        "using_default_local_database": _uses_default_workpaper_database(),
        "schema_ready": schema_status.ready,
        "schema_version": schema_status.schema_version,
        "expected_schema_version": schema_status.expected_schema_version,
        "blockers": blockers,
    }
