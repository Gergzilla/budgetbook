"""Builders for synthetic test data (no real statement data)."""

import pandas as pd

from budgetbook.utilities import db

# The frame contract the save/load functions are specified against: the new-schema column names,
# already normalized by the importer layer (ISO dates, signed integer cents, account chosen).
TX_COLUMNS = [
    "account_id",
    "transaction_date",
    "post_date",
    "name",
    "amount_cents",
    "category_id",
    "notes",
    "source",
    "import_hash",
]


def make_transactions(*rows: dict) -> pd.DataFrame:
    """Frame of TX_COLUMNS from partial dicts.  Defaults: account 1, no category, source csv, and
    a hash derived from the row position so distinct rows get distinct hashes."""
    out = []
    for i, row in enumerate(rows):
        full = {
            "account_id": 1,
            "transaction_date": "2026-03-10",
            "post_date": None,
            "name": f"MERCHANT {i}",
            "amount_cents": -1000,
            "category_id": None,
            "notes": None,
            "source": "csv",
        }
        full.update(row)
        full.setdefault(
            "import_hash",
            f"{full['account_id']}|{full['transaction_date']}|{full['name']}"
            f"|{full['amount_cents']}|{i}",
        )
        out.append(full)
    return pd.DataFrame(out, columns=TX_COLUMNS)


def add_account(name: str = "Checking", account_type: str = "checking") -> int:
    with db.get_connection() as conn:
        return conn.execute(
            "INSERT INTO accounts (name, account_type) VALUES (?, ?)", (name, account_type)
        ).lastrowid


def add_category(name: str) -> int:
    with db.get_connection() as conn:
        return conn.execute("INSERT INTO categories (name) VALUES (?)", (name,)).lastrowid


def insert_rows(frame: pd.DataFrame) -> None:
    """Seed transactions directly with SQL, bypassing the code under test."""
    cols = ", ".join(TX_COLUMNS)
    marks = ", ".join("?" for _ in TX_COLUMNS)
    with db.get_connection() as conn:
        conn.executemany(
            f"INSERT INTO transactions ({cols}) VALUES ({marks})",
            list(frame.itertuples(index=False, name=None)),
        )


def fetch_all(sql: str = "SELECT * FROM transactions ORDER BY id") -> list[tuple]:
    with db.get_connection() as conn:
        return conn.execute(sql).fetchall()
