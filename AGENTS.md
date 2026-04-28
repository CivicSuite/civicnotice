# CivicNotice Agent Board

## Source of Truth

- Upstream suite spec: `CivicSuite/civicsuite/docs/CivicSuiteUnifiedSpec.md`, especially the CivicNotice catalog entry and suite-wide non-negotiables.
- CivicNotice supports central notice registry stubs, deadline tracking, publication readiness tracking, channel planning, and public-records-aware export checklists.
- Staff own every decision.

## Hard Boundaries

- CivicNotice never decides legal sufficiency, publishes official notices, provides legal advice, writes back to publication systems, or updates a notice system of record.
- CivicNotice v0.1.1 must not call live LLMs or live agenda systems.
- deadline tracking, publication readiness tracking, channel planning, and records exports must be marked staff-review-required where applicable.
- CivicNotice depends on CivicCore; CivicCore must never depend on CivicNotice.
- CivicNotice may reference CivicClerk meeting concepts only through released APIs or deterministic sample data in v0.1.1.

## Verification

Run `bash scripts/verify-release.sh` before every push or release.
