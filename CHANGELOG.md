# Changelog

All notable changes to CivicNotice will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.2] - 2026-04-29

### Changed

- Moved CivicNotice to the `civiccore v0.9.0` release wheel.
- Replaced the local deadline-calculation implementation with the shared CivicCore notice deadline helper while preserving CivicNotice's disclaimer-bearing API and persistence shape.
- Updated verification gates, runtime metadata, landing-page copy, and release docs for the v0.1.2 release.

## [0.1.1] - 2026-04-28

### Added

- Optional SQLAlchemy-backed notice registry and deadline-plan records via `CIVICNOTICE_WORKPAPER_DB_URL`.
- Notice registry and deadline-plan retrieval endpoints for persisted records.

### Changed

- Dependency-alignment release: moved CivicNotice to `civiccore==0.3.0` while preserving the existing notice registry, deadline, publication-readiness, channel planning, records export, and public UI foundation.
- Updated CI, verification gates, package metadata, docs, runtime tests, landing page, and public UI labels for the v0.1.1 release.

## [0.1.0] - 2026-04-27

### Added

- FastAPI package/runtime foundation pinned to `civiccore==0.2.0`.
- notice registry helper using deterministic sample data.
- deadline tracking helper with staff-verification boundary.
- publication readiness tracking helper with review-required boundary.
- channel planning helper.
- Public-records export checklist for notice records.
- Accessible public sample UI at `/civicnotice` with browser QA coverage.
- Release gate: tests, docs, placeholder import guard, Ruff, and build artifact checks.

### Not Shipped

- legal sufficiency decisions, legal advice, live LLM calls, official notice publication, publication-system write-back, and notice system-of-record integrations.
