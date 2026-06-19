# CivicNotice

CivicNotice is the CivicSuite module for public hearing notices, legal notices, bid notices, vacancy notices, statutory publication deadlines, statutory rule checks, notice drafting templates, accessibility and language-readiness review, publication-readiness review, channel planning, subscriber delivery planning, archive/handoff packets, and notice-record export checklists.

Current state: **v0.2.0 notice compliance foundation release**, aligned to the `civiccore v1.2.0` release wheel. This repo ships a FastAPI package, health/root endpoints, documentation gates, deterministic sample notice registry, CivicCore-backed statutory deadline plans, deterministic statutory rule checks, notice drafting templates, accessibility and language-readiness review packets, optional database-backed registry/deadline/publication-proof workpapers, publication-readiness checklists, channel-planning helpers, subscriber delivery planning, archive/handoff packets, notice/records export checklist, and accessible public sample UI at `/civicnotice`. It does **not** ship legal sufficiency decisions, legal advice, live LLM calls, official notice publication, publication-system write-back, or notice system-of-record integrations.

## What CivicNotice Does

- Create sample notice registry stubs.
- Build statutory publication deadline reminder plans using the shared CivicCore notice helper.
- Check notice packets against deterministic staff-review rule packs for common notice types.
- Build staff-editable notice templates with required fields and unresolved placeholders.
- Build accessibility, plain-language, and human-approved translation readiness packets.
- Persist notice registry, deadline-plan, and publication-proof workpapers when `CIVICNOTICE_WORKPAPER_DB_URL` is configured.
- Store staff-reviewed publication proof packets linked to upstream Clerk, procurement, board, or manual source records.
- Assemble publication-readiness checklists for staff review.
- Plan notice channels and accessibility-review needs.
- Build subscriber delivery plans without sending notices or storing subscriber PII.
- Assemble archive/handoff packets for Clerk, Procure, Boards, Records, and manual staff files.
- Produce notice and records export checklists.
- Demonstrate a public notice-support UI at `/civicnotice`.

## What CivicNotice Does Not Do

- It does not decide legal sufficiency.
- It does not publish official notices.
- It does not provide legal advice.
- It does not call live LLMs in v0.2.0.
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
- `POST /api/v1/civicnotice/rule-check` checks a notice packet against deterministic staff-review rules.
- `POST /api/v1/civicnotice/templates` returns a staff-editable notice template.
- `POST /api/v1/civicnotice/publication-proof` stores a durable publication proof workpaper.
- `GET /api/v1/civicnotice/publication-proof/{proof_id}` retrieves a persisted publication proof workpaper.
- `POST /api/v1/civicnotice/publication-check` returns a publication-readiness checklist.
- `POST /api/v1/civicnotice/accessibility-review` returns accessibility and language-readiness flags.
- `POST /api/v1/civicnotice/channels` returns channel planning flags.
- `POST /api/v1/civicnotice/subscribers/plan` returns a subscriber delivery plan.
- `POST /api/v1/civicnotice/archive-packet` returns archive and handoff readiness for a notice file.
- `POST /api/v1/civicnotice/export` returns a notice and records export checklist.

## Start and Smoke-Check CivicNotice

Install the package with its development dependencies, start the ASGI app target `civicnotice.main:app`, and open the local `/health` and `/civicnotice` routes. A fresh user can reach the core stateless API and public sample UI without a database, model server, account, or API key.

Minimal workflow to smoke-check after startup:

1. Confirm `/health` reports `service: civicnotice`, version `0.2.0`, and CivicCore `1.2.0`.
2. Post a registry stub to `/api/v1/civicnotice/registry` without a database and confirm the response includes `record_id: null`, registry notes, and the staff-responsibility disclaimer.
3. Post a rule check to `/api/v1/civicnotice/rule-check` with a notice type, event date, publication dates, channels, content fields, and statutory basis.
4. Open `/civicnotice` and confirm the page is a static public sample with boundary copy, not an official publication workflow.

## Persistence and Durable Writes

Without `CIVICNOTICE_WORKPAPER_DB_URL`, CivicNotice runs in deterministic stateless mode: registry and deadline POST requests return transient payloads, persisted GET routes return actionable 503 responses, and publication-proof storage is unavailable.

With `CIVICNOTICE_WORKPAPER_DB_URL`, registry, deadline, and publication-proof workpapers are durable. Persistence-backed write routes also require `CIVICNOTICE_TRUSTED_WRITE_TOKEN` and the matching `X-CivicNotice-Write-Token` request header. This is a minimal trusted-mode guard for local deployments; it is not a replacement for a production identity system.

## Local Development

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
bash scripts/verify-release.sh
```

## License

Code is Apache License 2.0. Documentation is CC BY 4.0.
