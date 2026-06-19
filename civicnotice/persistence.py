from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import Engine, create_engine

from civicnotice.deadline_tracker import build_deadline_plan
from civicnotice.notice_registry import register_notice_stub
from civicnotice.publication_proof import record_publication_proof


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

publication_proof_records = sa.Table(
    "publication_proof_records",
    metadata,
    sa.Column("proof_id", sa.String(36), primary_key=True),
    sa.Column("notice_id", sa.String(160), nullable=False),
    sa.Column("notice_type", sa.String(160), nullable=False),
    sa.Column("source_module", sa.String(160), nullable=False),
    sa.Column("source_record_id", sa.String(160), nullable=False),
    sa.Column("channel", sa.String(160), nullable=False),
    sa.Column("published_at", sa.String(160), nullable=False),
    sa.Column("location", sa.Text(), nullable=False),
    sa.Column("confirmation_reference", sa.String(240), nullable=False),
    sa.Column("statutory_basis", sa.Text(), nullable=False),
    sa.Column("reviewer", sa.String(160), nullable=False),
    sa.Column("proof_notes", sa.JSON(), nullable=False),
    sa.Column("compliance_status", sa.String(160), nullable=False),
    sa.Column("disclaimer", sa.Text(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicnotice",
)


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
class StoredPublicationProof:
    proof_id: str
    notice_id: str
    notice_type: str
    source_module: str
    source_record_id: str
    channel: str
    published_at: str
    location: str
    confirmation_reference: str
    statutory_basis: str
    reviewer: str
    proof_notes: tuple[str, ...]
    compliance_status: str
    disclaimer: str
    created_at: datetime


class NoticeWorkpaperRepository:
    def __init__(self, *, db_url: str | None = None, engine: Engine | None = None) -> None:
        base_engine = engine or create_engine(db_url or "sqlite+pysqlite:///:memory:", future=True)
        if base_engine.dialect.name == "sqlite":
            self.engine = base_engine.execution_options(schema_translate_map={"civicnotice": None})
        else:
            self.engine = base_engine
            with self.engine.begin() as connection:
                connection.execute(sa.text("CREATE SCHEMA IF NOT EXISTS civicnotice"))
        metadata.create_all(self.engine)

    def create_notice_record(
        self, *, notice_id: str, notice_type: str, owner: str
    ) -> StoredNoticeRecord:
        record = register_notice_stub(notice_id=notice_id, notice_type=notice_type, owner=owner)
        stored = StoredNoticeRecord(
            str(uuid4()),
            record.notice_id,
            record.notice_type,
            record.owner,
            record.registry_notes,
            record.disclaimer,
            datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                notice_registry_records.insert().values(
                    record_id=stored.record_id,
                    notice_id=stored.notice_id,
                    notice_type=stored.notice_type,
                    owner=stored.owner,
                    registry_notes=list(stored.registry_notes),
                    disclaimer=stored.disclaimer,
                    created_at=stored.created_at,
                )
            )
        return stored

    def get_notice_record(self, record_id: str) -> StoredNoticeRecord | None:
        with self.engine.begin() as connection:
            row = (
                connection.execute(
                    sa.select(notice_registry_records).where(
                        notice_registry_records.c.record_id == record_id
                    )
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        data = dict(row)
        return StoredNoticeRecord(
            data["record_id"],
            data["notice_id"],
            data["notice_type"],
            data["owner"],
            tuple(data["registry_notes"]),
            data["disclaimer"],
            data["created_at"],
        )

    def create_deadline_plan(
        self, *, notice_type: str, event_date: date, lead_days: int = 10
    ) -> StoredDeadlinePlan:
        plan = build_deadline_plan(
            notice_type=notice_type, event_date=event_date, lead_days=lead_days
        )
        stored = StoredDeadlinePlan(
            str(uuid4()),
            plan.notice_type,
            plan.event_date,
            plan.reminders,
            plan.staff_review_required,
            plan.disclaimer,
            datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                deadline_plan_records.insert().values(
                    plan_id=stored.plan_id,
                    notice_type=stored.notice_type,
                    event_date=stored.event_date,
                    reminders=list(stored.reminders),
                    staff_review_required=stored.staff_review_required,
                    disclaimer=stored.disclaimer,
                    created_at=stored.created_at,
                )
            )
        return stored

    def get_deadline_plan(self, plan_id: str) -> StoredDeadlinePlan | None:
        with self.engine.begin() as connection:
            row = (
                connection.execute(
                    sa.select(deadline_plan_records).where(
                        deadline_plan_records.c.plan_id == plan_id
                    )
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        data = dict(row)
        return StoredDeadlinePlan(
            data["plan_id"],
            data["notice_type"],
            data["event_date"],
            tuple(data["reminders"]),
            data["staff_review_required"],
            data["disclaimer"],
            data["created_at"],
        )

    def create_publication_proof(
        self,
        *,
        notice_id: str,
        notice_type: str,
        source_module: str,
        source_record_id: str,
        channel: str,
        published_at: str,
        location: str,
        confirmation_reference: str,
        statutory_basis: str,
        reviewer: str,
    ) -> StoredPublicationProof:
        proof = record_publication_proof(
            notice_id=notice_id,
            notice_type=notice_type,
            source_module=source_module,
            source_record_id=source_record_id,
            channel=channel,
            published_at=published_at,
            location=location,
            confirmation_reference=confirmation_reference,
            statutory_basis=statutory_basis,
            reviewer=reviewer,
        )
        stored = StoredPublicationProof(
            str(uuid4()),
            proof.notice_id,
            proof.notice_type,
            proof.source_module,
            proof.source_record_id,
            proof.channel,
            proof.published_at,
            proof.location,
            proof.confirmation_reference,
            proof.statutory_basis,
            proof.reviewer,
            proof.proof_notes,
            proof.compliance_status,
            proof.disclaimer,
            datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                publication_proof_records.insert().values(
                    proof_id=stored.proof_id,
                    notice_id=stored.notice_id,
                    notice_type=stored.notice_type,
                    source_module=stored.source_module,
                    source_record_id=stored.source_record_id,
                    channel=stored.channel,
                    published_at=stored.published_at,
                    location=stored.location,
                    confirmation_reference=stored.confirmation_reference,
                    statutory_basis=stored.statutory_basis,
                    reviewer=stored.reviewer,
                    proof_notes=list(stored.proof_notes),
                    compliance_status=stored.compliance_status,
                    disclaimer=stored.disclaimer,
                    created_at=stored.created_at,
                )
            )
        return stored

    def get_publication_proof(self, proof_id: str) -> StoredPublicationProof | None:
        with self.engine.begin() as connection:
            row = (
                connection.execute(
                    sa.select(publication_proof_records).where(
                        publication_proof_records.c.proof_id == proof_id
                    )
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        data = dict(row)
        return StoredPublicationProof(
            data["proof_id"],
            data["notice_id"],
            data["notice_type"],
            data["source_module"],
            data["source_record_id"],
            data["channel"],
            data["published_at"],
            data["location"],
            data["confirmation_reference"],
            data["statutory_basis"],
            data["reviewer"],
            tuple(data["proof_notes"]),
            data["compliance_status"],
            data["disclaimer"],
            data["created_at"],
        )
