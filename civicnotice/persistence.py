from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import Engine, create_engine

from civicnotice.deadline_tracker import build_deadline_plan
from civicnotice.notice_registry import register_notice_stub


metadata = sa.MetaData()

notice_registry_records = sa.Table(
    "notice_registry_records",
    metadata,
    sa.Column("record_id", sa.String(36), primary_key=True),
    sa.Column("notice_id", sa.String(160), nullable=False),
    sa.Column("notice_type", sa.String(160), nullable=False),
    sa.Column("owner", sa.String(160), nullable=False),
    sa.Column("registry_notes", sa.JSON(), nullable=False),
    sa.Column("disclaimer", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicnotice",
)

deadline_plan_records = sa.Table(
    "deadline_plan_records",
    metadata,
    sa.Column("plan_id", sa.String(36), primary_key=True),
    sa.Column("notice_type", sa.String(160), nullable=False),
    sa.Column("event_date", sa.Date(), nullable=False),
    sa.Column("reminders", sa.JSON(), nullable=False),
    sa.Column("staff_review_required", sa.Boolean(), nullable=False),
    sa.Column("disclaimer", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicnotice",
)


staff_review_queue_records = sa.Table(
    "staff_review_queue_records",
    metadata,
    sa.Column("review_id", sa.String(36), primary_key=True),
    sa.Column("notice_id", sa.String(160), nullable=False),
    sa.Column("title", sa.String(500), nullable=False),
    sa.Column("reason", sa.Text(), nullable=False),
    sa.Column("status", sa.String(120), nullable=False),
    sa.Column("assigned_to", sa.String(255), nullable=True),
    sa.Column("resolution", sa.Text(), nullable=True),
    sa.Column("created_by", sa.String(160), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicnotice",
)


@dataclass(frozen=True)
class SchemaStatus:
    ready: bool
    schema_version: str
    expected_schema_version: str


@dataclass(frozen=True)
class StoredNoticeRecord:
    record_id: str
    notice_id: str
    notice_type: str
    owner: str
    registry_notes: tuple[str, ...]
    disclaimer: str
    created_at: datetime


@dataclass(frozen=True)
class StoredDeadlinePlan:
    plan_id: str
    notice_type: str
    event_date: date
    reminders: tuple[str, ...]
    staff_review_required: bool
    disclaimer: str
    created_at: datetime


@dataclass(frozen=True)
class StaffReviewQueueItem:
    review_id: str
    notice_id: str
    title: str
    reason: str
    status: str
    assigned_to: str | None
    resolution: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime


class NoticeWorkpaperRepository:
    expected_schema_version = "civicnotice-local-first-v1"

    def __init__(self, *, db_url: str | None = None, engine: Engine | None = None) -> None:
        base_engine = engine or create_engine(db_url or "sqlite+pysqlite:///:memory:", future=True)
        if base_engine.dialect.name == "sqlite":
            self.engine = base_engine.execution_options(schema_translate_map={"civicnotice": None})
        else:
            self.engine = base_engine
            with self.engine.begin() as connection:
                connection.execute(sa.text("CREATE SCHEMA IF NOT EXISTS civicnotice"))
        metadata.create_all(self.engine)

    def schema_status(self) -> SchemaStatus:
        try:
            with self.engine.begin() as connection:
                for table in (
                    notice_registry_records,
                    deadline_plan_records,
                    staff_review_queue_records,
                ):
                    connection.execute(sa.select(sa.func.count()).select_from(table)).scalar_one()
        except Exception:
            return SchemaStatus(
                ready=False,
                schema_version="unavailable",
                expected_schema_version=self.expected_schema_version,
            )
        return SchemaStatus(
            ready=True,
            schema_version=self.expected_schema_version,
            expected_schema_version=self.expected_schema_version,
        )

    def create_notice_record(self, *, notice_id: str, notice_type: str, owner: str) -> StoredNoticeRecord:
        record = register_notice_stub(notice_id=notice_id, notice_type=notice_type, owner=owner)
        stored = StoredNoticeRecord(str(uuid4()), record.notice_id, record.notice_type, record.owner, record.registry_notes, record.disclaimer, datetime.now(UTC))
        with self.engine.begin() as connection:
            connection.execute(notice_registry_records.insert().values(record_id=stored.record_id, notice_id=stored.notice_id, notice_type=stored.notice_type, owner=stored.owner, registry_notes=list(stored.registry_notes), disclaimer=stored.disclaimer, created_at=stored.created_at))
        return stored

    def get_notice_record(self, record_id: str) -> StoredNoticeRecord | None:
        with self.engine.begin() as connection:
            row = connection.execute(sa.select(notice_registry_records).where(notice_registry_records.c.record_id == record_id)).mappings().first()
        if row is None:
            return None
        data = dict(row)
        return StoredNoticeRecord(data["record_id"], data["notice_id"], data["notice_type"], data["owner"], tuple(data["registry_notes"]), data["disclaimer"], data["created_at"])

    def create_deadline_plan(self, *, notice_type: str, event_date: date, lead_days: int = 10) -> StoredDeadlinePlan:
        plan = build_deadline_plan(notice_type=notice_type, event_date=event_date, lead_days=lead_days)
        stored = StoredDeadlinePlan(str(uuid4()), plan.notice_type, plan.event_date, plan.reminders, plan.staff_review_required, plan.disclaimer, datetime.now(UTC))
        with self.engine.begin() as connection:
            connection.execute(deadline_plan_records.insert().values(plan_id=stored.plan_id, notice_type=stored.notice_type, event_date=stored.event_date, reminders=list(stored.reminders), staff_review_required=stored.staff_review_required, disclaimer=stored.disclaimer, created_at=stored.created_at))
        if stored.staff_review_required:
            self.create_staff_review_queue_item(
                notice_id=stored.notice_type,
                title=f"Deadline review: {stored.notice_type}",
                reason="Deadline plan requires staff/legal review before publication.",
                created_by="system",
            )
        return stored

    def get_deadline_plan(self, plan_id: str) -> StoredDeadlinePlan | None:
        with self.engine.begin() as connection:
            row = connection.execute(sa.select(deadline_plan_records).where(deadline_plan_records.c.plan_id == plan_id)).mappings().first()
        if row is None:
            return None
        data = dict(row)
        return StoredDeadlinePlan(data["plan_id"], data["notice_type"], data["event_date"], tuple(data["reminders"]), data["staff_review_required"], data["disclaimer"], data["created_at"])

    def create_staff_review_queue_item(
        self,
        *,
        notice_id: str,
        title: str,
        reason: str,
        created_by: str = "staff",
    ) -> StaffReviewQueueItem:
        now = datetime.now(UTC)
        item = StaffReviewQueueItem(
            review_id=str(uuid4()),
            notice_id=notice_id.strip() or "unassigned-notice",
            title=title.strip() or "Untitled notice review",
            reason=reason.strip() or "Notice staff review required.",
            status="open",
            assigned_to=None,
            resolution=None,
            created_by=created_by.strip() or "staff",
            created_at=now,
            updated_at=now,
        )
        with self.engine.begin() as connection:
            connection.execute(
                staff_review_queue_records.insert().values(
                    review_id=item.review_id,
                    notice_id=item.notice_id,
                    title=item.title,
                    reason=item.reason,
                    status=item.status,
                    assigned_to=item.assigned_to,
                    resolution=item.resolution,
                    created_by=item.created_by,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )
        return item

    def list_staff_review_queue_items(self, status: str | None = None) -> list[StaffReviewQueueItem]:
        query = sa.select(staff_review_queue_records).order_by(
            staff_review_queue_records.c.updated_at.desc()
        )
        if status:
            query = query.where(staff_review_queue_records.c.status == status)
        with self.engine.begin() as connection:
            rows = connection.execute(query).mappings().all()
        return [_row_to_staff_review(row) for row in rows]


def _row_to_staff_review(row: object) -> StaffReviewQueueItem:
    data = dict(row)
    return StaffReviewQueueItem(
        review_id=data["review_id"],
        notice_id=data["notice_id"],
        title=data["title"],
        reason=data["reason"],
        status=data["status"],
        assigned_to=data["assigned_to"],
        resolution=data["resolution"],
        created_by=data["created_by"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
    )
