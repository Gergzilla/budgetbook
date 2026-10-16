"""Specification of the db_handlers data functions against the NEW schema (schema version 1).

These tests describe what save_dataframe_to_db and load_db_to_dataframe must keep doing
(upsert without duplicating, filter by year / month) once they are moved onto db.get_connection()
and the new columns.  Today those functions still use the old column names, the import-time
default_database and the shared DatabaseSetup connection, so the specs are marked xfail (strict).
When the refactor lands each one turns into a failure that says "remove the marker".

The "plumbing" tests at the top are NOT xfail: they prove the fixtures and seeding helpers work,
so an xfail below can only come from the code under test.

Contract assumed (change here first if it is wrong):
  * frames carry helpers.TX_COLUMNS, already normalized: ISO dates, signed integer cents, an
    account_id and a caller-supplied import_hash (the importer layer computes it, TODO item 3);
  * save_dataframe_to_db(frame) -> None, one transaction for the whole frame;
  * load_db_to_dataframe({"year": "2026" | "All", "month": "Mar" | "Whole Year"}) keeps its
    current argument shape and returns one row per transaction, oldest first.

remove_duplicates has no specs here on purpose: see the note at the bottom.
"""

import sqlite3

import pytest

from budgetbook.utilities import db_handlers
from helpers import (
    add_account,
    add_category,
    fetch_all,
    insert_rows,
    make_transactions,
)

pending_refactor = pytest.mark.xfail(
    strict=True,
    reason="db_handlers not yet moved to the new schema (db-connect-schema section 8 items 5-7)",
)


# ---- plumbing: must pass today -------------------------------------------------------------


def test_tmp_db_is_new_schema_and_isolated(tmp_db):
    from budgetbook.vars import settings

    assert settings.get_db_path() == str(tmp_db)
    assert fetch_all("SELECT COUNT(*) FROM transactions") == [(0,)]


def test_seed_helpers_allow_identical_same_day_rows(tmp_db):
    add_account("Checking")
    insert_rows(make_transactions({"name": "A"}, {"name": "A"}))
    # identical same-day purchases are legitimate: distinct import_hash keeps both
    assert fetch_all("SELECT COUNT(*) FROM transactions") == [(2,)]


@pytest.fixture
def account(tmp_db):
    return add_account("Checking")


# ---- save_dataframe_to_db ------------------------------------------------------------------


@pending_refactor
def test_save_inserts_rows(account):
    frame = make_transactions({"name": "COFFEE", "amount_cents": -450}, {"name": "RENT"})
    db_handlers.save_dataframe_to_db(frame)
    rows = fetch_all("SELECT name, amount_cents FROM transactions ORDER BY id")
    assert rows == [("COFFEE", -450), ("RENT", -1000)]


@pending_refactor
def test_save_same_frame_twice_adds_no_rows(account):
    frame = make_transactions({"name": "COFFEE"}, {"name": "RENT"})
    db_handlers.save_dataframe_to_db(frame)
    db_handlers.save_dataframe_to_db(frame)
    assert fetch_all("SELECT COUNT(*) FROM transactions") == [(2,)]


@pending_refactor
def test_save_keeps_identical_same_day_purchases_with_distinct_hashes(account):
    # the flaw in the old UNIQUE(date, name, amount): both coffees must survive
    frame = make_transactions(
        {"name": "COFFEE", "amount_cents": -450}, {"name": "COFFEE", "amount_cents": -450}
    )
    db_handlers.save_dataframe_to_db(frame)
    assert fetch_all("SELECT COUNT(*) FROM transactions") == [(2,)]


@pending_refactor
def test_save_resave_updates_category_and_notes_of_existing_row(account):
    groceries = add_category("Groceries")
    frame = make_transactions({"name": "STORE"})
    db_handlers.save_dataframe_to_db(frame)
    frame["category_id"] = groceries
    frame["notes"] = "weekly shop"
    db_handlers.save_dataframe_to_db(frame)
    assert fetch_all("SELECT COUNT(*), category_id, notes FROM transactions") == [
        (1, groceries, "weekly shop")
    ]


@pending_refactor
def test_save_empty_values_never_overwrite_existing_ones(account):
    # decided: a re-import (blank category/notes) must not wipe what the user already entered.
    # Clearing details is a deliberate Admin-panel action, not a side effect of saving.
    groceries = add_category("Groceries")
    first = make_transactions({"name": "STORE", "category_id": groceries, "notes": "weekly shop"})
    db_handlers.save_dataframe_to_db(first)
    blank = make_transactions({"name": "STORE"})
    blank["import_hash"] = first["import_hash"]
    db_handlers.save_dataframe_to_db(blank)
    assert fetch_all("SELECT COUNT(*), category_id, notes FROM transactions") == [
        (1, groceries, "weekly shop")
    ]


@pending_refactor
def test_save_column_order_does_not_matter(account):
    frame = make_transactions({"name": "COFFEE", "amount_cents": -450})
    db_handlers.save_dataframe_to_db(frame[list(reversed(frame.columns))])
    assert fetch_all("SELECT name, amount_cents FROM transactions") == [("COFFEE", -450)]


@pending_refactor
def test_save_accepts_missing_values_in_optional_columns(account):
    frame = make_transactions({"name": "COFFEE", "post_date": None, "notes": float("nan")})
    db_handlers.save_dataframe_to_db(frame)
    assert fetch_all("SELECT post_date, notes FROM transactions") == [(None, None)]


@pending_refactor
def test_save_failure_rolls_back_whole_batch(account):
    good = make_transactions({"name": "GOOD"})
    bad = make_transactions({"name": "BAD", "account_id": 999})  # no such account
    frame = good.reset_index(drop=True)._append(bad, ignore_index=True)
    with pytest.raises(sqlite3.IntegrityError):  # foreign key on account_id
        db_handlers.save_dataframe_to_db(frame)
    assert fetch_all("SELECT COUNT(*) FROM transactions") == [(0,)]


# ---- load_db_to_dataframe ------------------------------------------------------------------


@pytest.fixture
def seeded(account):
    insert_rows(
        make_transactions(
            {"transaction_date": "2025-12-31", "name": "DEC25"},
            {"transaction_date": "2026-03-01", "name": "MAR_FIRST"},
            {"transaction_date": "2026-03-31", "name": "MAR_LAST"},
            {"transaction_date": "2026-04-01", "name": "APR_FIRST"},
            {"transaction_date": "2026-05-03", "name": "MAY_3"},
        )
    )


def _names(frame):
    return list(frame["name"])


@pending_refactor
def test_load_year_and_month(seeded):
    frame = db_handlers.load_db_to_dataframe({"year": "2026", "month": "Mar"})
    assert _names(frame) == ["MAR_FIRST", "MAR_LAST"]  # month boundaries are exact


@pending_refactor
def test_load_whole_year(seeded):
    frame = db_handlers.load_db_to_dataframe({"year": "2026", "month": "Whole Year"})
    assert _names(frame) == ["MAR_FIRST", "MAR_LAST", "APR_FIRST", "MAY_3"]


@pending_refactor
def test_load_all_years_whole_year_returns_everything_oldest_first(seeded):
    frame = db_handlers.load_db_to_dataframe({"year": "All", "month": "Whole Year"})
    assert len(frame) == 5
    assert _names(frame)[0] == "DEC25"


@pending_refactor
def test_load_month_across_all_years(seeded):
    frame = db_handlers.load_db_to_dataframe({"year": "All", "month": "Dec"})
    assert _names(frame) == ["DEC25"]


@pending_refactor
def test_load_empty_result_keeps_columns(seeded):
    frame = db_handlers.load_db_to_dataframe({"year": "2024", "month": "Whole Year"})
    assert frame.empty
    assert {"transaction_date", "name", "amount_cents"} <= set(frame.columns)


# ---- remove_duplicates: deliberately not specified yet ----------------------------------------
# Under the new schema import_hash UNIQUE already prevents re-import duplicates, and rows with
# the same (account, date, name, amount) can be genuine repeat purchases.  What "duplicate" means
# (and whether the function survives at all) is a design decision to make when it is refactored;
# it should call db.backup_database() first.  Specs are written then.
