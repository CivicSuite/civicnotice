# GauntletGate Report: CivicNotice 0.2.0

Date: 2026-06-19

Reviewed release: CivicNotice 0.2.0

Final pushed PR head reviewed by CI: 0ed06639a8f2c746337b6568586f73ca21b4111a

Product/runtime evidence source commit: 028a5954068d7423a1e1b6234723ddff5188908a

Report metadata note: report-only commits may follow the product/runtime evidence commit. GitHub CI on the final pushed PR head is the source of truth that those metadata commits did not break the release gate.

## Verdict

Gate passed for the reviewed product/runtime evidence, and GitHub CI is green for pushed PR head 0ed06639a8f2c746337b6568586f73ca21b4111a.

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
