# CivicNotice

CivicNotice is the CivicSuite module for public hearing notices, legal notices, bid notices, vacancy notices, statutory publication deadlines, publication-readiness review, channel planning, and notice-record export checklists.

Current state: **v0.1.2 notice compliance foundation release**, aligned to the `civiccore v0.9.0` release wheel. This repo ships a FastAPI package, health/root endpoints, documentation gates, deterministic sample notice registry, CivicCore-backed statutory deadline plans, optional database-backed registry/deadline workpapers, publication-readiness checklists, channel-planning helpers, notice/records export checklist, and accessible public sample UI at `/civicnotice`. It does **not** ship legal sufficiency decisions, legal advice, live LLM calls, official notice publication, publication-system write-back, or notice system-of-record integrations.

## What CivicNotice Does

- Create sample notice registry stubs.
- Build statutory publication deadline reminder plans using the shared CivicCore notice helper.
- Persist notice registry and deadline-plan workpapers when `CIVICNOTICE_WORKPAPER_DB_URL` is configured.
- Assemble publication-readiness checklists for staff review.
- Plan notice channels and accessibility-review needs.
- Produce notice and records export checklists.
- Demonstrate a public notice-support UI at `/civicnotice`.

## What CivicNotice Does Not Do

- It does not decide legal sufficiency.
- It does not publish official notices.
- It does not provide legal advice.
- It does not call live LLMs in v0.1.2.
- It does not write back to publication systems.
- It does not replace a notice system of record.

## API Surface

- `GET /` returns the shipped/planned boundary.
- `GET /health` returns package and CivicCore versions.
- `GET /civicnotice` returns the accessible public sample UI.
- `POST /api/v1/civicnotice/registry` returns a sample notice registry stub.
- `GET /api/v1/civicnotice/registry/{record_id}` retrieves a persisted notice registry record.
- `POST /api/v1/civicnotice/deadlines` returns statutory deadline reminders.
- `GET /api/v1/civicnotice/deadlines/{plan_id}` retrieves a persisted deadline plan.
- `POST /api/v1/civicnotice/publication-check` returns a publication-readiness checklist.
- `POST /api/v1/civicnotice/channels` returns channel planning flags.
- `POST /api/v1/civicnotice/export` returns a notice and records export checklist.

## Local Development

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
bash scripts/verify-release.sh
```

## License

Code is Apache License 2.0. Documentation is CC BY 4.0.
