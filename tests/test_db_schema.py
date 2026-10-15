"""Backup and schema versioning, against throwaway SQLite files only."""

import sqlite3

import pytest

from budgetbook.utilities import db, schema


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("PYBUDGET_DB", str(path))
    return path


def test_migrate_fresh_db_reaches_latest(db_path):
    assert schema.get_schema_version() == 0
    assert schema.migrate() == schema.LATEST_VERSION
    assert schema.get_schema_version() == schema.LATEST_VERSION
    with db.get_connection() as conn:
        tables = {
            r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    assert {"accounts", "categories", "transactions", "budgets", "merchant_rules"} <= tables


def test_migrate_is_idempotent(db_path):
    schema.migrate()
    assert schema.migrate() == schema.LATEST_VERSION


def test_migrate_refuses_old_layout(db_path):
    with db.get_connection() as conn:
        conn.execute("CREATE TABLE transactions (transaction_date TEXT)")
    with pytest.raises(RuntimeError):
        schema.migrate()


def test_foreign_keys_and_date_check_enforced(db_path):
    schema.migrate()
    with pytest.raises(sqlite3.IntegrityError):
        with db.get_connection() as conn:
            conn.execute(
                "INSERT INTO transactions (account_id, transaction_date, name, amount_cents)"
                " VALUES (999, '2026-01-01', 'x', -100)"
            )
    with db.get_connection() as conn:
        conn.execute("INSERT INTO accounts (name, account_type) VALUES ('a', 'checking')")
    with pytest.raises(sqlite3.IntegrityError):
        with db.get_connection() as conn:
            conn.execute(
                "INSERT INTO transactions (account_id, transaction_date, name, amount_cents)"
                " VALUES (1, 'Mar 05', 'x', -100)"
            )


def test_backup_missing_db_returns_none(db_path):
    assert db.backup_database() is None
    assert not db_path.exists()


def test_backup_copies_data_and_prunes(db_path, tmp_path):
    with db.get_connection() as conn:
        conn.execute("CREATE TABLE t (x)")
        conn.execute("INSERT INTO t VALUES (42)")
    bdir = tmp_path / "bk"
    paths = [db.backup_database(backup_dir=str(bdir), keep=2) for _ in range(4)]
    assert len(set(paths)) == 4
    remaining = sorted(bdir.iterdir())
    assert len(remaining) == 2
    assert [str(p) for p in remaining] == sorted(paths)[-2:]
    assert sqlite3.connect(remaining[-1]).execute("SELECT x FROM t").fetchone() == (42,)
