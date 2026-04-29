CivicNotice
===========

CivicNotice is the CivicSuite module for public hearing notices, legal notices, bid notices, vacancy notices, statutory publication deadlines, publication-readiness review, channel planning, and notice-record export checklists.

Current state: v0.1.2 notice compliance foundation release, aligned to the civiccore v0.9.0 release wheel. This repo ships a FastAPI package, health/root endpoints, documentation gates, deterministic sample notice registry, CivicCore-backed statutory deadline plans, optional database-backed registry/deadline workpapers via CIVICNOTICE_WORKPAPER_DB_URL, publication-readiness checklists, channel-planning helpers, notice/records export checklist, and accessible public sample UI at /civicnotice.

It does not ship legal sufficiency decisions, legal advice, live LLM calls, official notice publication, publication-system write-back, or notice system-of-record integrations.

What CivicNotice does:
- Create sample notice registry stubs.
- Build statutory publication deadline reminder plans using the shared CivicCore notice helper.
- Assemble publication-readiness checklists for staff review.
- Plan notice channels and accessibility-review needs.
- Produce notice and records export checklists.
- Demonstrate a public notice-support UI at /civicnotice.

API surface:
- GET /
- GET /health
- GET /civicnotice
- POST /api/v1/civicnotice/registry
- GET /api/v1/civicnotice/registry/{record_id}
- POST /api/v1/civicnotice/deadlines
- GET /api/v1/civicnotice/deadlines/{plan_id}
- POST /api/v1/civicnotice/publication-check
- POST /api/v1/civicnotice/channels
- POST /api/v1/civicnotice/export

License: Apache License 2.0 for code; CC BY 4.0 for documentation.
