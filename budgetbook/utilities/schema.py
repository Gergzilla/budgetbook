#!/usr/bin/python
"""Schema versioning: PRAGMA user_version plus an ordered list of numbered migrations.

A database at user_version N has had migrations 1..N applied.  A new migration is appended to
MIGRATIONS and never edited afterwards.  Version 1 is the redesigned schema created from scratch
(see roadmap/TODO-foundation.md, Schema).  There is no data migration from the old pre-version
schema (version 0): that data is test data and is purged, see TODO-foundation.md, Migration.
"""

from . import db

_SCHEMA_V1 = """
CREATE TABLE accounts (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    account_type  TEXT NOT NULL,
    identifier    TEXT,
    institution   TEXT,
    is_active     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE categories (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE
);

CREATE TABLE transactions (
    id               INTEGER PRIMARY KEY,
    account_id       INTEGER NOT NULL REFERENCES accounts(id),
    transaction_date TEXT    NOT NULL
        CHECK (transaction_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    post_date        TEXT
        CHECK (post_date IS NULL
               OR post_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    name             TEXT    NOT NULL,
    amount_cents     INTEGER NOT NULL,
    category_id      INTEGER REFERENCES categories(id),
    is_transfer      INTEGER NOT NULL DEFAULT 0,
    transfer_peer_id INTEGER REFERENCES transactions(id),
    notes            TEXT,
    source           TEXT,
    import_hash      TEXT UNIQUE,
    created_at       TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_tx_date ON transactions(transaction_date);
CREATE INDEX idx_tx_account ON transactions(account_id);

CREATE TABLE budgets (
    id             INTEGER PRIMARY KEY,
    category_id    INTEGER NOT NULL REFERENCES categories(id),
    amount_cents   INTEGER NOT NULL,
    effective_from TEXT NOT NULL,
    UNIQUE (category_id, effective_from)
);

CREATE TABLE merchant_rules (
    id              INTEGER PRIMARY KEY,
    pattern         TEXT NOT NULL,
    match_type      TEXT NOT NULL DEFAULT 'exact',
    category_id     INTEGER NOT NULL REFERENCES categories(id),
    times_confirmed INTEGER NOT NULL DEFAULT 1,
    UNIQUE (pattern, match_type, category_id)
);
"""

# Each entry is the SQL script that takes the database from version index to index + 1.
MIGRATIONS: list[str] = [_SCHEMA_V1]
LATEST_VERSION = len(MIGRATIONS)


def get_schema_version(db_path: str | None = None) -> int:
    """The database's PRAGMA user_version (0 for a new or pre-versioning database)."""
    with db.get_connection(db_path) as conn:
        return conn.execute("PRAGMA user_version").fetchone()[0]


def migrate(db_path: str | None = None) -> int:
    """Apply any missing migrations in order and return the resulting version.

    Refuses a database newer than this code understands.  If the database holds any tables
    (version 0 with the old layout) migration 1 would clash with them, so that is refused too:
    purge or point at a fresh file instead.  A backup is taken before changing a database that
    already has a version."""
    current = get_schema_version(db_path)
    if current > LATEST_VERSION:
        raise RuntimeError(
            f"Database schema version {current} is newer than this app supports "
            f"({LATEST_VERSION})."
        )
    if current == LATEST_VERSION:
        return current

    if current == 0:
        with db.get_connection(db_path) as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' "
                "AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        if tables:
            raise RuntimeError(
                "Database has tables but no schema version (old layout). Back it up and "
                "purge it, or set PYBUDGET_DB to a fresh file."
            )
    else:
        db.backup_database(db_path)

    for version in range(current + 1, LATEST_VERSION + 1):
        # executescript commits first and runs outside the get_connection transaction, so the
        # script and the version bump are one explicit transaction to stay all-or-nothing.
        with db.get_connection(db_path) as conn:
            conn.executescript(
                "BEGIN;\n"
                + MIGRATIONS[version - 1]
                + f"\nPRAGMA user_version = {version};\nCOMMIT;"
            )
    return LATEST_VERSION
