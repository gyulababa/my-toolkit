# app/sqlite/dbkit/db.py
from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DbConfig:
    path: Path


def open_db(cfg: DbConfig) -> sqlite3.Connection:
    cfg.path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(cfg.path), check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=3000;")
    return conn


def default_db_config() -> DbConfig:
    path = os.environ.get("OPS_DB_PATH", "./data/ops.db")
    return DbConfig(path=Path(path))
