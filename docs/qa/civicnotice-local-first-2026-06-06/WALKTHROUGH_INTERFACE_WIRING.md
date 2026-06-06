# CivicNotice local-first walkthrough and interface wiring audit

Date: 2026-06-06
Scope: CivicNotice local-first runtime, public UI, staff UI, API wiring, persistence, and suite integration contracts.

## Result

PASS. No blocker, critical, major, minor, or nit findings were found in this walkthrough.

## Runtime exercised

- Local app: `http://127.0.0.1:18866`
- Runtime data: local SQLite through `CIVICNOTICE_DATA_DIR`
- Screenshots:
  - `desktop-public.png`
  - `desktop-staff.png`
  - `mobile-public.png`
  - `mobile-staff.png`
- API evidence: `api-evidence.json`

## Product model

CivicNotice is a public notice administration module. It supports notice registry intake, statutory deadline reminders, publication-readiness checks, channel planning, staff review queues, records export context, and suite-visible integration contracts. It explicitly does not determine legal sufficiency, publish official notices, provide legal advice, call live LLMs, write back to publication systems, or replace the notice system of record.

## Routes and workflows checked

- `GET /health` returned HTTP 200 with CivicNotice `0.1.2` and CivicCore `1.2.0`.
- `GET /api/v1/civicnotice/readiness` returned HTTP 200 with `ready=true`, `schema_ready=true`, and `using_default_local_database=true`.
- `GET /api/v1/civicnotice/integration-contracts` returned all required local-first contracts: notice registry, staff review queue, publication packet, and records export.
- `GET /civicnotice` rendered the public notice-support page on desktop and mobile without layout overlap.
- `GET /civicnotice/staff` rendered the staff review page on desktop and mobile without layout overlap after the mobile header padding fix.
- `POST /api/v1/civicnotice/registry` created a notice registry record.
- `GET /api/v1/civicnotice/registry/{record_id}` retrieved the created notice registry record.
- `POST /api/v1/civicnotice/deadlines` created a persisted deadline plan and flagged staff review.
- `GET /api/v1/civicnotice/deadlines/{plan_id}` retrieved the created deadline plan.
- `GET /api/v1/civicnotice/staff/reviews` without staff auth returned the expected staff-key configuration error.
- `POST /api/v1/civicnotice/publication-check` returned a publication-readiness checklist.
- `POST /api/v1/civicnotice/channels` returned channel planning and accessibility review notes.
- `POST /api/v1/civicnotice/export` returned a records export checklist and retention note.

## Wiring verdict

The public UI is conservative and honest about module boundaries. The staff UI exposes the workflows implemented by the backend: notice intake, deadline review creation, and queue loading. The API supports local persistence by default, and the readiness endpoint proves the schema is present before the suite can treat the module as ready.

The staff queue is protected by CivicCore `staff_key_gate`; keyed behavior is covered by tests because the walkthrough server intentionally did not expose a staff secret in process startup.

## Evidence-backed source cross-check

- Readiness and integration contracts are implemented in `civicnotice/main.py`.
- Staff queue endpoints are implemented in `civicnotice/main.py`.
- Default local SQLite pathing is implemented in `civicnotice/main.py`.
- Staff review persistence and schema checks are implemented in `civicnotice/persistence.py`.
- Deadline plans auto-queue staff review when review is required in `civicnotice/persistence.py`.
- Behavioral tests cover readiness/contracts, staff-key queue access, auto-queued deadline review, and placeholder import guard behavior.

## Test commands

- `python -m pytest -q`: passed, 20 tests.
- `bash scripts/verify-release.sh`: passed, including tests, docs, placeholder import guard, Ruff, and build artifact checks.
- `python -m py_compile civicnotice/main.py civicnotice/persistence.py civicnotice/public_ui.py`: passed.

## Findings

None.
