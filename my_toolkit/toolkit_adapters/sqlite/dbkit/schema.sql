BEGIN;

CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT OR IGNORE INTO meta(key, value) VALUES ('schema_version', '1');

-- Current document row (one per (kind, doc_id))
CREATE TABLE IF NOT EXISTS docs (
  kind             TEXT NOT NULL,
  doc_id           TEXT NOT NULL,

  title            TEXT NOT NULL DEFAULT '',
  body             TEXT NOT NULL DEFAULT '',
  tags             TEXT NOT NULL DEFAULT '',
  assignment_group TEXT NOT NULL DEFAULT '',
  meta_json        TEXT NOT NULL DEFAULT '{}',

  deleted          INTEGER NOT NULL DEFAULT 0,

  created_at       TEXT NOT NULL,
  updated_at       TEXT NOT NULL,
  rev              INTEGER NOT NULL DEFAULT 1,

  PRIMARY KEY(kind, doc_id)
);

-- Immutable revision log (append-only)
CREATE TABLE IF NOT EXISTS doc_revisions (
  kind        TEXT NOT NULL,
  doc_id      TEXT NOT NULL,
  rev         INTEGER NOT NULL,
  payload_json TEXT NOT NULL,
  created_at  TEXT NOT NULL,
  note        TEXT NOT NULL DEFAULT '',

  PRIMARY KEY(kind, doc_id, rev),
  FOREIGN KEY(kind, doc_id) REFERENCES docs(kind, doc_id) ON DELETE CASCADE
);

-- ===== FTS5 (optional but recommended) =====
CREATE VIRTUAL TABLE IF NOT EXISTS fts_docs
USING fts5(kind, doc_id, title, body, tags, assignment_group);

-- Keep FTS in sync (simple strategy: delete+insert on changes)
CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON docs BEGIN
  INSERT INTO fts_docs(kind, doc_id, title, body, tags, assignment_group)
  VALUES (new.kind, new.doc_id, new.title, new.body, new.tags, new.assignment_group);
END;

CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE OF title, body, tags, assignment_group, deleted ON docs BEGIN
  DELETE FROM fts_docs WHERE kind = old.kind AND doc_id = old.doc_id;
  INSERT INTO fts_docs(kind, doc_id, title, body, tags, assignment_group)
  VALUES (new.kind, new.doc_id, new.title, new.body, new.tags, new.assignment_group);
END;

CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON docs BEGIN
  DELETE FROM fts_docs WHERE kind = old.kind AND doc_id = old.doc_id;
END;

COMMIT;
