"""FastAPI runtime foundation for CivicNotice."""

from datetime import date

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from civicnotice import __version__
from civicnotice.channel_plan import plan_notice_channels
from civicnotice.deadline_tracker import build_deadline_plan
from civicnotice.notice_registry import register_notice_stub
from civicnotice.public_ui import render_public_lookup_page
from civicnotice.publication_check import build_publication_checklist
from civicnotice.records_export import build_notice_records_export


app = FastAPI(
    title="CivicNotice",
    version=__version__,
    description="Public hearing, legal notice, bid notice, vacancy notice, and statutory publication deadline support for CivicSuite.",
)


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
            "publication-readiness checklist, channel planning, records export checklist, and public UI "
            "foundation are online; official legal sufficiency decisions, official publication, legal "
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
    return register_notice_stub(
        notice_id=request.notice_id,
        notice_type=request.notice_type,
        owner=request.owner,
    ).__dict__


@app.post("/api/v1/civicnotice/deadlines")
def deadline_plan(request: DeadlineRequest) -> dict[str, object]:
    return build_deadline_plan(
        notice_type=request.notice_type,
        event_date=request.event_date,
        lead_days=request.lead_days,
    ).__dict__


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
