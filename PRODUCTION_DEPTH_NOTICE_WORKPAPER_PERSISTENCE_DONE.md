# Production Depth: Notice Workpaper Persistence

## Summary

CivicNotice now supports optional SQLAlchemy-backed notice registry and deadline-plan records through `CIVICNOTICE_WORKPAPER_DB_URL`.

## Shipped

- `NoticeWorkpaperRepository` with schema-aware SQLAlchemy tables.
- Persisted notice registry records with `record_id`.
- Persisted deadline-plan records with `plan_id`.
- Retrieval endpoints:
  - `GET /api/v1/civicnotice/registry/{record_id}`
  - `GET /api/v1/civicnotice/deadlines/{plan_id}`
- Actionable `503` guidance when persistence is not configured.

## Still Not Shipped

- Official legal sufficiency decisions.
- Official notice publication.
- Legal advice.
- Publication-system write-back.
- Notice system-of-record integrations.
