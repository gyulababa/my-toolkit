# app/sqlite/dbkit/store.py
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .types import Doc, DocKey, DocRevision, SearchHit


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _doc_from_row(r: sqlite3.Row) -> Doc:
    return Doc(
        kind=r["kind"],
        doc_id=r["doc_id"],
        title=r["title"],
        body=r["body"],
        tags=r["tags"],
        meta_json=r["meta_json"],
        assignment_group=r["assignment_group"],
        deleted=int(r["deleted"]),
        created_at=r["created_at"],
        updated_at=r["updated_at"],
        rev=int(r["rev"]),
    )


@dataclass
class SqliteDocStore:
    conn: sqlite3.Connection

    # -------- schema / migrate --------

    def migrate_if_needed(self) -> None:
        v = self._get_schema_version()
        if v >= 1:
            return
        sql = (Path(__file__).with_name("schema.sql")).read_text(encoding="utf-8")  # type: ignore[name-defined]
        self.conn.executescript(sql)
        self.conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES ('migrated_at', datetime('now'))")
        self.conn.commit()

    def _get_schema_version(self) -> int:
        row = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='meta'"
        ).fetchone()
        if not row:
            return 0
        v = self.conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
        return int(v["value"]) if v else 0

    # -------- CRUD + revisions --------

    def create_doc(
        self,
        key: DocKey,
        *,
        title: str = "",
        body: str = "",
        tags: str = "",
        assignment_group: str = "",
        meta: Optional[Dict[str, Any]] = None,
        note: str = "create",
    ) -> Doc:
        now = _now_iso()
        meta_json = json.dumps(meta or {}, ensure_ascii=False)

        self.conn.execute(
            """
            INSERT INTO docs(kind, doc_id, title, body, tags, assignment_group, meta_json, deleted, created_at, updated_at, rev)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, 1)
            """,
            (key.kind, key.doc_id, title, body, tags, assignment_group, meta_json, now, now),
        )

        payload = self._build_payload(key, title, body, tags, assignment_group, meta_json, deleted=0)
        self.conn.execute(
            """
            INSERT INTO doc_revisions(kind, doc_id, rev, payload_json, created_at, note)
            VALUES (?, ?, 1, ?, ?, ?)
            """,
            (key.kind, key.doc_id, payload, now, note),
        )

        self.conn.commit()
        return self.get_doc(key, include_deleted=True)  # should exist

    def update_doc(
        self,
        key: DocKey,
        *,
        title: Optional[str] = None,
        body: Optional[str] = None,
        tags: Optional[str] = None,
        assignment_group: Optional[str] = None,
        meta_patch: Optional[Dict[str, Any]] = None,
        note: str = "update",
    ) -> Doc:
        cur = self.get_doc(key, include_deleted=True)
        if cur is None:
            raise KeyError("not_found")

        cur_meta = json.loads(cur.meta_json or "{}")
        if meta_patch:
            cur_meta.update(meta_patch)
        meta_json = json.dumps(cur_meta, ensure_ascii=False)

        new_title = cur.title if title is None else title
        new_body = cur.body if body is None else body
        new_tags = cur.tags if tags is None else tags
        new_ag = cur.assignment_group if assignment_group is None else assignment_group

        now = _now_iso()
        new_rev = cur.rev + 1

        self.conn.execute(
            """
            UPDATE docs
            SET title=?, body=?, tags=?, assignment_group=?, meta_json=?,
                updated_at=?, rev=?
            WHERE kind=? AND doc_id=?
            """,
            (new_title, new_body, new_tags, new_ag, meta_json, now, new_rev, key.kind, key.doc_id),
        )

        payload = self._build_payload(key, new_title, new_body, new_tags, new_ag, meta_json, deleted=cur.deleted)
        self.conn.execute(
            """
            INSERT INTO doc_revisions(kind, doc_id, rev, payload_json, created_at, note)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (key.kind, key.doc_id, new_rev, payload, now, note),
        )

        self.conn.commit()
        return self.get_doc(key, include_deleted=True)  # updated

    def soft_delete(self, key: DocKey, *, note: str = "soft_delete") -> None:
        cur = self.get_doc(key, include_deleted=True)
        if cur is None:
            raise KeyError("not_found")
        if cur.deleted == 1:
            return

        now = _now_iso()
        new_rev = cur.rev + 1

        self.conn.execute(
            "UPDATE docs SET deleted=1, updated_at=?, rev=? WHERE kind=? AND doc_id=?",
            (now, new_rev, key.kind, key.doc_id),
        )
        payload = self._build_payload(key, cur.title, cur.body, cur.tags, cur.assignment_group, cur.meta_json, deleted=1)
        self.conn.execute(
            "INSERT INTO doc_revisions(kind, doc_id, rev, payload_json, created_at, note) VALUES (?, ?, ?, ?, ?, ?)",
            (key.kind, key.doc_id, new_rev, payload, now, note),
        )
        self.conn.commit()

    def restore(self, key: DocKey, *, note: str = "restore") -> None:
        cur = self.get_doc(key, include_deleted=True)
        if cur is None:
            raise KeyError("not_found")
        if cur.deleted == 0:
            return

        now = _now_iso()
        new_rev = cur.rev + 1

        self.conn.execute(
            "UPDATE docs SET deleted=0, updated_at=?, rev=? WHERE kind=? AND doc_id=?",
            (now, new_rev, key.kind, key.doc_id),
        )
        payload = self._build_payload(key, cur.title, cur.body, cur.tags, cur.assignment_group, cur.meta_json, deleted=0)
        self.conn.execute(
            "INSERT INTO doc_revisions(kind, doc_id, rev, payload_json, created_at, note) VALUES (?, ?, ?, ?, ?, ?)",
            (key.kind, key.doc_id, new_rev, payload, now, note),
        )
        self.conn.commit()

    def get_doc(self, key: DocKey, *, include_deleted: bool = False) -> Optional[Doc]:
        if include_deleted:
            row = self.conn.execute(
                "SELECT * FROM docs WHERE kind=? AND doc_id=?",
                (key.kind, key.doc_id),
            ).fetchone()
        else:
            row = self.conn.execute(
                "SELECT * FROM docs WHERE kind=? AND doc_id=? AND deleted=0",
                (key.kind, key.doc_id),
            ).fetchone()
        return _doc_from_row(row) if row else None

    def list_revisions(self, key: DocKey, *, limit: int = 50) -> List[DocRevision]:
        rows = self.conn.execute(
            """
            SELECT rev, payload_json, created_at, note
            FROM doc_revisions
            WHERE kind=? AND doc_id=?
            ORDER BY rev DESC
            LIMIT ?
            """,
            (key.kind, key.doc_id, limit),
        ).fetchall()
        return [DocRevision(rev=int(r["rev"]), payload_json=r["payload_json"], created_at=r["created_at"], note=r["note"]) for r in rows]

    def restore_revision(self, key: DocKey, rev: int, *, note: str = "restore_revision") -> Doc:
        r = self.conn.execute(
            "SELECT payload_json FROM doc_revisions WHERE kind=? AND doc_id=? AND rev=?",
            (key.kind, key.doc_id, rev),
        ).fetchone()
        if not r:
            raise KeyError("revision_not_found")

        payload = json.loads(r["payload_json"])
        # payload is your canonical stored shape; we apply it as a new update (new revision)
        return self.update_doc(
            key,
            title=payload.get("title", ""),
            body=payload.get("body", ""),
            tags=payload.get("tags", ""),
            assignment_group=payload.get("assignment_group", ""),
            meta_patch=payload.get("meta") or {},
            note=note,
        )

    # -------- Search (FTS5) --------

    def search(self, q: str, *, kind: Optional[str] = None, limit: int = 20) -> List[SearchHit]:
        q = (q or "").strip()
        if not q:
            return []

        params: List[Any] = []
        sql = """
        SELECT kind, doc_id, title,
               snippet(fts_docs, 3, '[', ']', '…', 12) AS snippet
        FROM fts_docs
        WHERE fts_docs MATCH ?
        """
        params.append(q)

        if kind:
            sql += " AND kind = ?"
            params.append(kind)

        sql += " LIMIT ?"
        params.append(limit)

        rows = self.conn.execute(sql, params).fetchall()
        return [SearchHit(kind=r["kind"], doc_id=r["doc_id"], title=r["title"], snippet=r["snippet"]) for r in rows]

    # -------- internals --------

    def _build_payload(
        self,
        key: DocKey,
        title: str,
        body: str,
        tags: str,
        assignment_group: str,
        meta_json: str,
        *,
        deleted: int,
    ) -> str:
        meta = json.loads(meta_json or "{}")
        payload = {
            "kind": key.kind,
            "doc_id": key.doc_id,
            "title": title,
            "body": body,
            "tags": tags,
            "assignment_group": assignment_group,
            "meta": meta,
            "deleted": int(deleted),
        }
        return json.dumps(payload, ensure_ascii=False)
