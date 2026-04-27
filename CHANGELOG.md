# Changelog

All notable changes to CivicNotice will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
