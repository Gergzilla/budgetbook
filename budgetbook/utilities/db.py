#!/usr/bin/python
"""Single owner of SQLite connections for the application."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from ..vars import settings


def _open_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")  # per-connection setting, must be set every time
    return conn


@contextmanager
def get_connection(db_path: str | None = None):
    """Yield a connection; commit on success, roll back on error, always close.
    The path is resolved at call time (see settings.get_db_path)."""
    conn = _open_connection(db_path or settings.get_db_path())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def backup_database(
    db_path: str | None = None, backup_dir: str | None = None, keep: int = 10
) -> str | None:
    """Write a consistent, timestamped copy of the database using SQLite's backup API.

    The copy goes to `<db folder>/backups` unless backup_dir is given.  Only the newest `keep`
    backups of this database are retained.  Returns the backup path, or None if the database
    file does not exist (nothing to back up)."""
    src_path = Path(db_path or settings.get_db_path())
    if not src_path.exists():
        return None
    dest_dir = Path(backup_dir) if backup_dir else src_path.parent / "backups"
    dest_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    dest_path = dest_dir / f"{src_path.stem}-{stamp}{src_path.suffix}"

    src = sqlite3.connect(src_path)
    dest = sqlite3.connect(dest_path)
    try:
        src.backup(dest)
    finally:
        dest.close()
        src.close()

    # names sort chronologically because of the timestamp, so oldest are first
    existing = sorted(dest_dir.glob(f"{src_path.stem}-*{src_path.suffix}"))
    for old in existing[: max(len(existing) - keep, 0)]:
        old.unlink()
    return str(dest_path)
