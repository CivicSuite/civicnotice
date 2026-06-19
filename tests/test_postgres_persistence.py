from __future__ import annotations

from datetime import date
import os

import pytest
import sqlalchemy as sa

from civicnotice.persistence import NoticeWorkpaperRepository


@pytest.mark.skipif(
    not os.environ.get("CIVICNOTICE_POSTGRES_TEST_URL"),
    reason="CIVICNOTICE_POSTGRES_TEST_URL is required for PostgreSQL persistence coverage.",
)
def test_postgres_persistence_creates_schema_and_round_trips_workpapers() -> None:
    db_url = os.environ["CIVICNOTICE_POSTGRES_TEST_URL"]
    engine = sa.create_engine(db_url, future=True)
    with engine.begin() as connection:
        connection.execute(sa.text("DROP SCHEMA IF EXISTS civicnotice CASCADE"))
    engine.dispose()

    repository = NoticeWorkpaperRepository(db_url=db_url)
    record = repository.create_notice_record(
        notice_id="PG-N-1", notice_type="planning hearing", owner="Clerk"
    )
    plan = repository.create_deadline_plan(
        notice_type="planning hearing", event_date=date(2026, 6, 15)
    )
    proof = repository.create_publication_proof(
        notice_id="PG-N-1",
        notice_type="planning hearing",
        source_module="civicclerk",
        source_record_id="meeting-pg-1",
        channel="newspaper",
        published_at="2026-05-20T09:00:00-06:00",
        location="Daily Gazette",
        confirmation_reference="PG-AFF-1",
        statutory_basis="staff-entered basis",
        reviewer="City Clerk",
    )

    assert repository.get_notice_record(record.record_id).notice_id == "PG-N-1"
    assert repository.get_deadline_plan(plan.plan_id).event_date == date(2026, 6, 15)
    assert repository.get_publication_proof(proof.proof_id).source_module == "civicclerk"

    with repository.engine.begin() as connection:
        schema_exists = connection.execute(
            sa.text("select exists(select 1 from information_schema.schemata where schema_name='civicnotice')")
        ).scalar_one()
    repository.engine.dispose()
    assert schema_exists is True
