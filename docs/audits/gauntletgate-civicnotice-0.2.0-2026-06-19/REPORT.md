# GauntletGate Report: CivicNotice 0.2.0

Date: 2026-06-19

Reviewed release: CivicNotice 0.2.0

Final reviewed commit: 028a5954b4a7cc119a5b46e219f47e2101aa328c

## Verdict

Pending final CI confirmation for commit 028a5954b4a7cc119a5b46e219f47e2101aa328c.

## Gate Scope

- Principal engineering review
- UI/UX review
- Technical writing review
- Test engineering review
- QA/runtime evidence review

## Issues Found and Resolved

- Inert public UI controls were removed from `/civicnotice`; the public page is now a static sample with boundary copy and no misleading draft controls.
- Unknown statutory-rule notice types no longer silently fall back to `general notice`; common public-hearing aliases normalize to `planning hearing`, and unsupported types return 422 with supported choices.
- `/docs` and `/openapi.json` are now documented in first-use surfaces and linked from the docs landing page when served by FastAPI.
- Configured-but-unavailable persistence now returns actionable 503 responses instead of raw 500 errors.
- The release gate now requires `CIVICNOTICE_POSTGRES_TEST_URL` and verifies that the selected Python interpreter can see it before tests run.
- Historical QA notes are marked historical, and obsolete cloud-sync evidence paths were replaced with repository-relative references.

## Verification Evidence

- `artifacts/verify-release-postgres.log` shows the full release gate passing with PostgreSQL coverage, CivicCore wheel SHA verification, docs verification, placeholder import checks, Ruff, build artifacts, and 34 passing tests with no skips.
- `artifacts/api-smoke.json` shows root, health, public UI, OpenAPI, no-DB dependency behavior, notice-type aliasing, and unsupported notice type rejection.
- `artifacts/environment-attestation.txt` records the reviewed git head and runtime environment.
- `artifacts/public-ui.html`, `artifacts/openapi.json`, `artifacts/root.json`, `artifacts/health.json`, and `artifacts/dependency-absent-no-db.json` preserve runtime smoke outputs.

## Remaining Watchlist

None. No deferred findings are allowed for this stage.
