CivicNotice
===========

CivicNotice is the CivicSuite module for public hearing notices, legal notices, bid notices, vacancy notices, statutory publication deadlines, statutory rule checks, notice drafting templates, accessibility and language-readiness review, publication-readiness review, channel planning, subscriber delivery planning, archive/handoff packets, and notice-record export checklists.

Current state: v0.2.0 notice compliance foundation release, aligned to the civiccore v1.2.0 release wheel. This repo ships a FastAPI package, health/root endpoints, documentation gates, deterministic sample notice registry, CivicCore-backed statutory deadline plans, deterministic statutory rule checks, notice drafting templates, accessibility and language-readiness review packets, optional database-backed registry/deadline/publication-proof workpapers via CIVICNOTICE_WORKPAPER_DB_URL, publication-readiness checklists, channel-planning helpers, subscriber delivery planning, archive/handoff packets, notice/records export checklist, and accessible public sample UI at /civicnotice.

It does not ship legal sufficiency decisions, legal advice, live LLM calls, official notice publication, publication-system write-back, or notice system-of-record integrations.

What CivicNotice does:
- Create sample notice registry stubs.
- Build statutory publication deadline reminder plans using the shared CivicCore notice helper.
- Check notice packets against deterministic staff-review rule packs for common notice types.
- Build staff-editable notice templates with required fields and unresolved placeholders.
- Build accessibility, plain-language, and human-approved translation readiness packets.
- Persist notice registry, deadline-plan, and publication-proof workpapers when CIVICNOTICE_WORKPAPER_DB_URL is configured.
- Store staff-reviewed publication proof packets linked to upstream source records.
- Assemble publication-readiness checklists for staff review.
- Plan notice channels and accessibility-review needs.
- Build subscriber delivery plans without sending notices or storing subscriber PII.
- Assemble archive/handoff packets for Clerk, Procure, Boards, Records, and manual staff files.
- Produce notice and records export checklists.
- Demonstrate a public notice-support UI at /civicnotice.

API surface:
- GET /
- GET /health
- GET /civicnotice
- GET /docs
- GET /openapi.json
- POST /api/v1/civicnotice/registry
- GET /api/v1/civicnotice/registry/{record_id}
- POST /api/v1/civicnotice/deadlines
- GET /api/v1/civicnotice/deadlines/{plan_id}
- POST /api/v1/civicnotice/rule-check
- POST /api/v1/civicnotice/templates
- POST /api/v1/civicnotice/publication-proof
- GET /api/v1/civicnotice/publication-proof/{proof_id}
- POST /api/v1/civicnotice/publication-check
- POST /api/v1/civicnotice/accessibility-review
- POST /api/v1/civicnotice/channels
- POST /api/v1/civicnotice/subscribers/plan
- POST /api/v1/civicnotice/archive-packet
- POST /api/v1/civicnotice/export

Start and smoke-check CivicNotice:

Install the package with development dependencies, start the ASGI app target civicnotice.main:app, and open the local /health and /civicnotice routes. A fresh user can reach the core stateless API and public sample UI without a database, model server, account, or API key.

Minimal smoke check:
1. Confirm /health reports service civicnotice, version 0.2.0, and CivicCore 1.2.0.
2. Post a registry stub to /api/v1/civicnotice/registry without a database and confirm record_id is null with registry notes and the staff-responsibility disclaimer.
3. Open /docs or /openapi.json to inspect accepted fields, then post a rule check to /api/v1/civicnotice/rule-check with a supported notice type, event date, publication dates, channels, content fields, and statutory basis. Unsupported notice types return a 422 response with supported choices.
4. Open /civicnotice and confirm the page is a static public sample with boundary copy, not an official publication workflow.

Persistence and durable writes:

Without CIVICNOTICE_WORKPAPER_DB_URL, CivicNotice runs in deterministic stateless mode: registry and deadline POST requests return transient payloads, persisted GET routes return actionable 503 responses, and publication-proof storage is unavailable.

With CIVICNOTICE_WORKPAPER_DB_URL, registry, deadline, and publication-proof workpapers are durable. Persistence-backed write routes also require CIVICNOTICE_TRUSTED_WRITE_TOKEN and the matching X-CivicNotice-Write-Token request header. This is a minimal trusted-mode guard for local deployments; it is not a replacement for a production identity system.

Release gate:

The full release gate requires CIVICNOTICE_POSTGRES_TEST_URL so PostgreSQL persistence coverage cannot be skipped. Plain unit tests may still run without PostgreSQL for local development.

License: Apache License 2.0 for code; CC BY 4.0 for documentation.
