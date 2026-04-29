"""FastAPI runtime foundation for CivicNotice."""

from datetime import date
import os

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from civicnotice import __version__
from civicnotice.channel_plan import plan_notice_channels
from civicnotice.deadline_tracker import build_deadline_plan
from civicnotice.notice_registry import register_notice_stub
from civicnotice.persistence import NoticeWorkpaperRepository, StoredDeadlinePlan, StoredNoticeRecord
from civicnotice.public_ui import render_public_lookup_page
from civicnotice.publication_check import build_publication_checklist
from civicnotice.records_export import build_notice_records_export


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


class ChannelRequest(BaseModel):
    notice_type: str
    audience: str


class RecordsExportRequest(BaseModel):
    notice_id: str
    title: str
    format: str = "markdown"


@app.get("/")
def root() -> dict[str, str]:
    """Return current product state without overstating unshipped behavior."""

    return {
        "name": "CivicNotice",
        "version": __version__,
        "status": "notice compliance foundation",
        "message": (
            "CivicNotice package, API foundation, sample notice registry, deadline plans, "
            "publication-readiness checklist, channel planning, records export checklist, optional "
            "database-backed registry/deadline workpapers, and public UI foundation are online; official "
            "legal sufficiency decisions, official publication, legal "
            "advice, live LLM calls, publication-system write-back, and notice system-of-record integrations "
            "are not implemented yet."
        ),
        "next_step": "Post-v0.1.1 roadmap: statutory rule packs, CivicClerk/CivicProcure/CivicNotice handoffs, and publication proof queues",
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
        return _stored_notice_response(_get_workpaper_repository().create_notice_record(
            notice_id=request.notice_id,
            notice_type=request.notice_type,
            owner=request.owner,
        ))
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
        raise HTTPException(status_code=503, detail={"message":"CivicNotice workpaper persistence is not configured.","fix":"Set CIVICNOTICE_WORKPAPER_DB_URL to retrieve persisted notice registry records."})
    stored = _get_workpaper_repository().get_notice_record(record_id)
    if stored is None:
        raise HTTPException(status_code=404, detail={"message":"Notice registry record not found.","fix":"Use a record_id returned by POST /api/v1/civicnotice/registry."})
    return _stored_notice_response(stored)


@app.post("/api/v1/civicnotice/deadlines")
def deadline_plan(request: DeadlineRequest) -> dict[str, object]:
    if _workpaper_database_url() is not None:
        return _stored_deadline_response(_get_workpaper_repository().create_deadline_plan(
            notice_type=request.notice_type,
            event_date=request.event_date,
            lead_days=request.lead_days,
        ))
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
        raise HTTPException(status_code=503, detail={"message":"CivicNotice workpaper persistence is not configured.","fix":"Set CIVICNOTICE_WORKPAPER_DB_URL to retrieve persisted deadline plans."})
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
    return {"record_id": stored.record_id, "notice_id": stored.notice_id, "notice_type": stored.notice_type, "owner": stored.owner, "registry_notes": list(stored.registry_notes), "disclaimer": stored.disclaimer, "created_at": stored.created_at.isoformat()}

def _stored_deadline_response(stored: StoredDeadlinePlan) -> dict[str, object]:
    return {"plan_id": stored.plan_id, "notice_type": stored.notice_type, "event_date": stored.event_date.isoformat(), "reminders": list(stored.reminders), "staff_review_required": stored.staff_review_required, "disclaimer": stored.disclaimer, "created_at": stored.created_at.isoformat()}
