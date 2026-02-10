# app/sqlite

Lightweight SQLite helpers for app-level document storage.

## dbkit
- `db.py`: connection setup and default `OPS_DB_PATH`.
- `schema.sql`: base schema for docs, revisions, and FTS.
- `store.py`: CRUD/revision/search helpers over the schema.
- `types.py`: dataclasses for document types.
