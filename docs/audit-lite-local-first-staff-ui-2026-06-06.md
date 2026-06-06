# Audit Lite - CivicNotice local-first staff runtime

Date: 2026-06-06
Scope: CivicNotice default local persistence, staff review queue, staff UI, integration contracts, dependency alignment, docs, and tests.

## TL;DR

Ship this slice to the full module gate. CivicNotice now works as a local-first standalone module: it creates and retrieves notice registry records, deadline plan workpapers, staff review queue items, readiness metadata, and suite integration contracts without requiring an external database. Staff queue routes use the CivicCore staff-key gate, and the module exposes suite handoffs for CivicClerk, CivicBoards, CivicProcure, CivicRecords AI, and CivicLegal.

## Severity rollup

- Blocker: 0
- Critical: 0
- Major: 0
- Minor: 0
- Nit: 0

## Findings

No findings.

## What's working

- `civicnotice.main` now exposes `/ready`, `/api/v1/civicnotice/readiness`, `/civicnotice/staff`, `/api/v1/civicnotice/integration-contracts`, and staff review queue endpoints.
- `civicnotice.persistence` now creates default local SQLite-backed schema for notice records, deadline plans, and staff review records through `CIVICNOTICE_DATA_DIR`.
- Staff-only queue routes use `CIVICNOTICE_STAFF_API_KEY` and `X-CivicNotice-Staff-Key` through CivicCore `staff_key_gate`.
- The placeholder-import guard permits the real CivicCore v1.2.0 auth dependency while still failing forbidden placeholder imports.
- README, user manual, docs landing page, and changelog describe the local-first/staff runtime and suite handoff boundaries.
- Behavioral tests passed: `python -m pytest -q`, `bash scripts/verify-release.sh`, and `python -m py_compile civicnotice/main.py civicnotice/persistence.py civicnotice/public_ui.py`.

## Watch items

Full stage gate still needs a browser walkthrough and audit-full over the finished module, then umbrella pinning and clean-machine proof after the active CivicBoards gate clears.

## Escalation recommendation

No escalation needed for this slice. Continue with the full module gate and umbrella installer integration sequencing.
