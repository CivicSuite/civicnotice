# Security

CivicNotice is early-stage software. Current version: `0.2.0`. Do not deploy it as a system of record until a release explicitly says it is production-ready.

## Supported Versions

| Version | Security support |
| --- | --- |
| 0.2.x | Supported for private vulnerability reports |
| 0.1.x | Best-effort only |

## Private Reporting

Report suspected vulnerabilities through GitHub private vulnerability reporting for the `CivicSuite/civicnotice` repository when available. If private reporting is unavailable, contact the repository owner privately before opening a public issue.

Do not include live municipal secrets, resident data, publication affidavits, subscriber lists, credentials, access tokens, database dumps, or exploit details in public issues, pull requests, screenshots, or discussion threads.

## What To Include

- Affected CivicNotice version and commit, if known.
- Whether `CIVICNOTICE_WORKPAPER_DB_URL` or `CIVICNOTICE_TRUSTED_WRITE_TOKEN` was configured.
- Steps to reproduce with synthetic data only.
- Expected and observed behavior.
- Impact assessment, including whether durable workpaper writes or public notice artifacts are exposed.

## Response Expectations

Maintainers should acknowledge private reports within 5 business days, triage severity, and coordinate a fix or advisory before public disclosure when the report is valid. Critical issues affecting durable writes, stored workpapers, or sensitive data handling should be prioritized before feature work.

## Deployment Boundary

CivicNotice 0.2.0 is designed for local, staff-reviewed municipal workflows. Persistence-backed writes require the trusted write token, but this token is only a minimal local guard. Production deployments should place CivicNotice behind the city's normal authentication, authorization, TLS, logging, backup, and network controls.
