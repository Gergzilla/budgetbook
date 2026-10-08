# DB connection module: proposed design

Explains `TODO-foundation.md`, **Code structure, bullet 1** ("One connection owner"). Nothing here is applied yet.
Examples are written against the **current** schema (`transaction_date`, `transaction_amount`, `tags`, ...) so they
can be adopted before the schema redesign. Versions assumed are the pinned ones (Python >= 3.10, pandas 2.2.0).

## 1. What exists today

Connections to `db.sqlite3` are opened in five different ways (all in the live code):

| Where | How | Problem |
| --- | --- | --- |
| `vars/settings.py:10` | `dbconnect = sqlite3.connect(expensedb)` at import time | No other live code uses it. Opens (and creates) the DB file just by importing settings. |
| `db_handlers.DatabaseSetup` (class body, lines 44-50) | `dbconnect` and `write_cursor` shared at class level | Connects at import, never closed. One shared cursor is reused by every call. |
| `save_dataframe_to_db` | borrows `DatabaseSetup.dbconnect` / `write_cursor` | Commits once at the end, but an error mid-loop leaves earlier rows pending on the shared connection. |
| `load_db_to_dataframe`, `query_by_month`, `query_by_yearly_table`, `remove_duplicates` | each calls `sqlite3.connect(...)` itself | Never closed. Each function repeats the setup, so any rule (like foreign keys) must be copied everywhere. |
| `DatabaseSetup.create_database` | bare `sqlite3.connect(...)` | Result discarded and never closed. |

Consequences: unclosed connections can hold the file locked on Windows (a problem when you want to back up or
delete the file), changes made through one connection may not be visible to another until committed, and there is
no single place to turn on settings or add logging.

## 2. Why online advice conflicts

Most of the contradictory advice comes from a few real subtleties in Python's `sqlite3`:

1. **`with conn:` does not close the connection.** It only commits on success or rolls back on an exception.
   Many tutorials show `with sqlite3.connect(...) as conn:` and imply it closes. It does not, which is why you also
   see `conn.close()` or `contextlib.closing(...)`.
2. **One shared connection vs one per operation.** Both are valid. A single long-lived connection is fine for a
   single-threaded desktop app, but a shared *cursor* is not. For a small app, opening a connection per operation
   is simple, cheap (SQLite is a local file) and avoids stale state. That is the design below.
3. **Threads.** By default a connection can only be used from the thread that created it
   (`check_same_thread=True`). Advice to set it to `False` applies to multi-threaded servers. Your Qt app runs DB
   calls on the GUI thread, so leave the default. Per-operation connections also avoid the issue if you ever add worker threads.
4. **`PRAGMA foreign_keys` is per connection.** It defaults to OFF every time. A connection factory is the only
   reliable place to turn it on.
5. **The 3.12 `autocommit=` parameter.** Newer docs describe it, but it does not exist on 3.10/3.11 (your
   `requires-python`). The design below avoids it and uses the default transaction behavior.

## 3. The proposed module

New file `budgetbook/utilities/db.py`. It is the only code in the project that calls `sqlite3.connect`.

```python
"""Single owner of SQLite connections for the application."""

import sqlite3
from contextlib import contextmanager

from ..vars import settings


def _open_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")  # per-connection setting, must be set every time
    return conn


@contextmanager
def get_connection(db_path: str = settings.expensedb):
    """Yield a connection; commit on success, roll back on error, always close."""
    conn = _open_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### Component by component

- **`_open_connection`**: the one place a connection is created. Anything every connection needs lives here:
  today `PRAGMA foreign_keys = ON` (needed once `category_id` references `categories`), later possibly
  `row_factory`, a busy timeout, or logging. It is private (leading underscore) so nothing else bypasses it.
- **`@contextmanager`** (from the standard library `contextlib`): turns a generator function into something
  usable with `with`. Code before `yield` is the "enter" step, the `yield` hands the connection to the caller's
  `with` block, and code after it runs when the block ends.
- **`yield conn`**: the caller's block runs here. If it finishes normally, execution continues to `conn.commit()`.
- **`except Exception: rollback(); raise`**: if the caller's block raises, nothing is half-saved, and the error
  still propagates so callers (and your logger) see it. Use a bare `raise` so the traceback is kept.
- **`finally: conn.close()`**: runs on success and on error, fixing the unclosed-connection leaks.
- **Default argument `db_path=settings.expensedb`**: callers normally pass nothing. Tests and the migration
  script can pass a different path (a temp file or the new DB file) without touching global state. Because the
  default is evaluated once at import, it is fine as long as the path is not changed at runtime.

What it deliberately does **not** do: no global connection, no class-level state, no shared cursor, no
`check_same_thread=False`.

### Usage pattern

```python
from .db import get_connection

with get_connection() as conn:
    rows = conn.execute("SELECT ... WHERE x = ?", (value,)).fetchall()
```

One `with` block is one transaction. Everything inside it is committed together or not at all, so group related
writes in a single block (for example all rows of an import) rather than one block per row.

## 4. Updating existing functions

These rewrite the existing functions in `db_handlers.py`, with the same names and return types where possible so
callers in `__main__.py` don't change, except where noted.

### 4.1 `save_dataframe_to_db`

Before: borrows the shared class connection and cursor, loops with `iterrows()`, commits at the end.

After:

```python
def save_dataframe_to_db(input_frame: pd.DataFrame) -> None:
    """Upsert every row of the dataframe in a single transaction."""
    columns = [
        "transaction_date", "post_date", "transaction_name",
        "transaction_amount", "tags", "notes",
    ]
    rows = list(input_frame[columns].itertuples(index=False, name=None))
    with get_connection() as conn:
        conn.executemany(
            "INSERT INTO transactions (transaction_date, post_date, transaction_name,"
            " transaction_amount, tags, notes) VALUES (?,?,?,?,?,?) "
            "ON CONFLICT (transaction_date, transaction_name, transaction_amount) "
            "DO UPDATE SET post_date = excluded.post_date, tags = excluded.tags,"
            " notes = excluded.notes",
            rows,
        )
```

- `executemany` runs one statement for all rows, which is shorter and faster than `iterrows()`.
- If any row fails (for example a constraint error), the whole batch is rolled back instead of leaving some
  rows saved. Previously the earlier rows stayed pending on the shared connection.
- The `DO UPDATE SET` no longer rewrites the three columns that make up the conflict key. They are identical by
  definition when the conflict fires, so setting them was redundant.
- The `columns` list also fixes the column order explicitly, so a DataFrame with the columns in a different order still saves correctly.

### 4.2 `load_db_to_dataframe`

Before: opens its own connection, never closes it. After, only the connection handling changes:

```python
def load_db_to_dataframe(load_query: dict) -> pd.DataFrame:
    ...  # year_match / month_match logic unchanged
    with get_connection() as conn:
        return pd.read_sql(
            db_query, conn, params={"year": year_match, "month": month_match}
        )
```

`return` inside the `with` is fine: the DataFrame is built before the block exits, then the connection closes.
`pd.read_sql` accepts a plain `sqlite3` connection in pandas 2.2.0. (The date-matching logic itself is
covered by TODO item 2.)

### 4.3 `remove_duplicates`

Before: builds SQL with f-strings, prints the cursor object, never closes. After:

```python
def remove_duplicates() -> int:
    """Delete duplicate transactions, keeping the first row of each group. Returns rows removed."""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM transactions WHERE rowid NOT IN ("
            " SELECT MIN(rowid) FROM transactions"
            " GROUP BY transaction_date, transaction_name, transaction_amount)"
        )
        return cursor.rowcount
```

The table name is now fixed in the statement instead of passed in, which also removes the f-string SQL (TODO Code
structure bullet 2). Returning the row count lets the Admin tab tell the user how many rows were removed.
Callers in `__main__.py` that ignore the return value keep working. If you need other tables later, validate the
name against a fixed set rather than formatting it in.

### 4.4 `DatabaseSetup` check/create (bullet 1 and bullet 4 together)

Before: class-level connection and cursor; `poll_master_table()` returns `(bool, str)`, but
`button_check_db_clicked` tests the whole tuple (always truthy), and `create_budget_table` re-checks the stale
`table_check` after creating the table, so it reports failure.

After, as plain functions with one return type each:

```python
def table_exists(table: str = "transactions") -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
        ).fetchone()
    return row is not None


def create_budget_table() -> bool:
    """Create the transactions table if missing. Returns True if it was created."""
    if table_exists():
        return False
    with get_connection() as conn:
        conn.executescript(
            "CREATE TABLE transactions (transaction_date TEXT, post_date TEXT, "
            "transaction_name TEXT, transaction_amount REAL, tags TEXT, notes TEXT, "
            "UNIQUE(transaction_date, transaction_name, transaction_amount))"
        )
    return table_exists()
```

The menu handlers then build their messages from simple booleans, for example
`"Database Check Complete!" if db_handlers.table_exists() else "Table not found..."`.
`executescript` issues its own commit first, so use it only for DDL. Use `execute` for data.

### 4.5 `create_database`

`sqlite3.connect()` creates the file if it does not exist, so creating the DB is just opening and closing one
connection: `with get_connection(): pass`. Keep the `os.path.exists` check if you still want the "already exists"
message.

## 5. Cleanup this enables

After the functions above are moved over:

- Delete the class-level `dbconnect`/`write_cursor` from `DatabaseSetup`.
- Delete `dbconnect = sqlite3.connect(expensedb)` from `vars/settings.py`. I found no live code using it, only
  `db_handlers` reads `settings.expensedb` (the path). Search for `settings.dbconnect` before removing.
- Remove `import sqlite3` from every module except `db.py` and `settings.py` (only if `settings.py` stops using it).
- Importing the app no longer creates or opens `db.sqlite3` as a side effect, so a missing DB is created only when
  the user chooses "Create Database" or a function actually needs it.

## 6. Suggested order of changes

*Superseded by [section 8, Order of Operations](#8-order-of-operations), which lists the exact files and functions.*

1. Add `utilities/db.py` (no behavior change by itself).
2. Move `load_db_to_dataframe` and `remove_duplicates` over first. They are the simplest and have no shared state.
3. Move `save_dataframe_to_db`, then the table check/create functions, updating the menu handlers in
   `__main__.py` for the new return values.
4. Remove the old shared connections.
5. Manually test: Create Database, Create Table, import and save a CSV, load a month, delete duplicates, with
   `db.sqlite3` backed up first.

## 7. Open questions

- **Row access style.** Add `conn.row_factory = sqlite3.Row` in `_open_connection` if you want column names on
  fetched rows (`row["name"]`). Not needed for `pd.read_sql`, so the default stays off.
- **Test database.** The `db_path` parameter lets a future `tests/` folder (gitignored today) point at a temp file.
- **Where the path lives.** Replacing the hardcoded `D:\...` path (Code structure bullet 5) is a separate change
  that only touches `settings.py`, since `db.py` reads the path from there.

## 8. Order of Operations

Reference steps as "section 8 item N". Each item is one self-contained change with its own test, so you can
implement and verify one at a time. Items 1-4 are the low-risk part (settings cleanup, the new module, and the
database validation functions). Items 5-7 touch the real I/O. Items 8-10 are cleanup. Back up `db.sqlite3` before
item 3 and again before item 7.

Decisions already made: the hardcoded `db_path` in `settings.expensedb` stays as is (the new module reads it, and a
user-chosen path comes later), and `windows/budget_main.py` is not touched (see the table below).

### Files and functions touched

| File | Functions / names changed | Item |
| --- | --- | --- |
| `budgetbook/vars/settings.py` | remove `mydb`, `dbconnect`, `import sqlite3`, two commented-out lines | 1 |
| `budgetbook/utilities/db.py` (**new**) | `_open_connection`, `get_connection` | 2 |
| `budgetbook/utilities/db_handlers.py` | add `table_exists`, `create_budget_table`, `create_database` (module-level) | 3 |
| `budgetbook/__main__.py` | `button_check_db_clicked`, `button_create_table_clicked`, `button_create_database_clicked` | 4 |
| `budgetbook/utilities/db_handlers.py` | `load_db_to_dataframe` | 5 |
| `budgetbook/utilities/db_handlers.py`, `budgetbook/__main__.py` | `remove_duplicates`, `button_delete_duplicates_clicked` (optional) | 6 |
| `budgetbook/utilities/db_handlers.py` | `save_dataframe_to_db` | 7 |
| `budgetbook/utilities/db_handlers.py` | `query_by_month`, `query_by_yearly_table` (optional, connection handling only) | 8 |
| `budgetbook/utilities/db_handlers.py` | delete `DatabaseSetup` class, unused imports and `default_database` if unused | 9 |
| `CLAUDE.md`, this file | update the DB layer notes | 10 |

**Intentionally not changed:**

- `windows/budget_main.py`: it is a copy of `__main__.py` and still calls `db_handlers.DatabaseSetup.*`. It is not
  wired in, and you asked that `windows/` stay as is until the refactor. It will stop working once item 9 removes
  `DatabaseSetup`. Apply the same handler edits from item 4 to it when you resume that refactor.
- `utilities/handlers.py`: `write_expense_to_db` (calls the missing `db_handlers.write_to_expenses`) and
  `create_query_by_month` are dead legacy code, left alone per the no-removals rule.
- `gui_handlers.py`, the importers, `logger.py`, and `settings.month_dict` / `year_list` / `expenseTable`.

### 1. Clean up `vars/settings.py`

- **Files / functions:** `vars/settings.py` only.
- **Change:**
  - Remove `mydb`. It duplicates `expensedb` and is only referenced under `utilities/deprecated/`.
  - Remove `dbconnect = sqlite3.connect(expensedb)`. Nothing live uses it, and it opens the database on import.
  - Remove `import sqlite3` (no longer needed) and the two commented-out lines (`# mydb = ...`, `# mytable = ...`).
  - Keep `import os`, `expensedb` (hardcoded path), `expenseTable` (read by `db_handlers`), `month_dict` and `year_list`.
- **Result:**

  ```python
  import os

  expensedb = os.path.join("D:\\", "scripts", "pybudget", "budgetbook", "db.sqlite3")
  expenseTable = "transactions"
  ```

- **Verify:** run the app. It should start exactly as before. The database file should still get created on startup
  for now, because `DatabaseSetup` still connects when `db_handlers` is imported (that goes away in item 9).

### 2. Add `utilities/db.py`

- **Files / functions:** new file `budgetbook/utilities/db.py` with `_open_connection` and `get_connection`, exactly as in section 3.
- **Change:** no existing code uses it yet, so behavior is unchanged.
- **Verify:** from the repo root, `python -c "from budgetbook.utilities import db; print(db.get_connection)"`
  imports cleanly, then run the app to confirm nothing else changed.

### 3. Add the new database validation functions to `db_handlers.py`

- **Files / functions:** `db_handlers.py`: add three module-level functions next to the old `DatabaseSetup` methods
  (the class stays for now, so nothing breaks while you test). Add `from ..utilities import db` to the imports.
- **Change:**

  ```python
  def table_exists(table: str = expenseTable) -> bool:
      """True if the database file exists and contains the given table."""
      if not os.path.exists(default_database):
          logger.warning("Database file not found at %s", default_database)
          return False
      with db.get_connection() as conn:
          row = conn.execute(
              "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
          ).fetchone()
      logger.info("Table %s %s", table, "found" if row else "not found")
      return row is not None


  def create_budget_table() -> bool:
      """Create the transactions table if missing. True if created, False if it already existed."""
      if table_exists():
          logger.info("No action required, table already exists.")
          return False
      with db.get_connection() as conn:
          conn.executescript(
              "CREATE TABLE transactions (transaction_date TEXT, post_date TEXT, "
              "transaction_name TEXT, transaction_amount REAL, tags TEXT, notes TEXT, "
              "UNIQUE(transaction_date, transaction_name, transaction_amount))"
          )
      logger.info("Table created")
      return True


  def create_database() -> bool:
      """Create the database file if missing. True if created, False if it already existed."""
      if os.path.exists(default_database):
          logger.info("Database already exists at %s", default_database)
          return False
      with db.get_connection():
          pass  # opening a connection creates the empty database file
      logger.warning("Database file created at %s", default_database)
      return True
  ```

- **Differences from section 4.4:** `table_exists` checks `os.path.exists` first, because `sqlite3.connect` creates
  an empty file as a side effect. Without the guard, "Verify Database" on a missing database would create it.
  Messages are logged here instead of returned, and the Qt message boxes are built in item 4.
- **Name clash:** these share names with the `DatabaseSetup` static methods, but one is inside the class and one
  at module level, so both can exist until item 9.
- **Verify:** the app still works unchanged. No caller uses the new functions yet.

### 4. Switch the three menu handlers in `__main__.py`

- **Files / functions:** `__main__.py`: `MainWindow.button_check_db_clicked`, `button_create_table_clicked`,
  `button_create_database_clicked`.
- **Change:**

  ```python
  def button_check_db_clicked(self) -> None:
      """Reports whether the transactions table exists in the database"""
      check_msg = QMessageBox()
      if db_handlers.table_exists():
          check_msg.setText("Database Check Complete!")
      else:
          check_msg.setText(
              "Database Check failed, the database or transactions table was not found."
          )
      check_msg.exec()

  def button_create_table_clicked(self) -> None:
      """Creates the transactions table if it is missing"""
      created = db_handlers.create_budget_table()
      check_msg = QMessageBox()
      check_msg.setWindowTitle("Transaction Table Creation")
      check_msg.setText(
          "Transaction table created." if created
          else "No action required, table already exists."
      )
      check_msg.exec()

  def button_create_database_clicked(self) -> None:
      """Creates the database file if it is missing"""
      created = db_handlers.create_database()
      check_msg = QMessageBox()
      check_msg.setWindowTitle("Database Status")
      check_msg.setText(
          "Database file created." if created else "Database already exists."
      )
      check_msg.exec()
  ```

- **Notes:** this fixes the always-true tuple test in the check handler. If the database file is missing,
  "Create Transaction Table" will create the file too (SQLite behavior), which is acceptable. Real SQLite errors
  (locked file, corruption) are not caught here and will show as a traceback in the console and the log. Friendlier
  error dialogs can come later.
- **Verify (this is the main checkpoint for the validation functions):** copy `db.sqlite3` somewhere safe, then
  test each case from a clean state by renaming the live file:
  1. With the real database present: **Verify Database** reports success. **Create Transaction Table** says the
     table already exists. **Create Database** says it already exists.
  2. Rename `db.sqlite3` away: **Verify Database** reports failure and **no file appears** (confirms the guard).
  3. **Create Database**: reports created, and an empty `db.sqlite3` appears. If no file appears, tell me, since
     the fallback is to issue a trivial write such as `PRAGMA user_version = 0` inside the `with` block.
  4. **Verify Database**: still fails (file exists, no table). **Create Transaction Table**: reports created.
     **Verify Database**: succeeds.
  5. Restore your real database.

### 5. Move `load_db_to_dataframe` to `get_connection`

- **Files / functions:** `db_handlers.py`: `load_db_to_dataframe` only. The `year_match` / `month_match` logic is
  unchanged. Replace the `sqlite3.connect(default_database)` line and the `pd.read_sql` call with the
  `with db.get_connection() as conn: return pd.read_sql(...)` form from section 4.2.
- **Callers (unchanged):** `button_load_from_db_clicked` and `_generate_report_chart` in `__main__.py`.
- **Verify:** Data tab -> Load Month from Database, and Reports tab -> Run Report. Compare the rows and the pie
  chart against what you saw before the change.

### 6. Move `remove_duplicates` to `get_connection`

- **Files / functions:** `db_handlers.py`: `remove_duplicates` (new form in section 4.3: no parameters, fixed table
  name, returns the number of rows removed). Optional: `__main__.py` `button_delete_duplicates_clicked` to show
  the count in a message box. The existing call `db_handlers.remove_duplicates()` still works unchanged.
- **Verify:** use a copy of the database. Count rows, run Delete Duplicates, and confirm the count only drops if
  duplicates existed. Run it again and confirm it removes 0.

### 7. Move `save_dataframe_to_db` to `get_connection` (highest risk)

- **Files / functions:** `db_handlers.py`: `save_dataframe_to_db` only, using the `executemany` form from section
  4.1. The caller `save_to_database` in `__main__.py` is unchanged.
- **Before starting:** back up `db.sqlite3` and write down the row count.
- **Verify:**
  1. Import a CSV and Save to Database. The row count should increase by the number of new rows.
  2. Import and save the **same** file again. The count should not change (the upsert key still matches).
  3. Edit the tags or notes on a row, save, and reload the month to confirm the edit persisted.
  4. Force an error (for example temporarily rename the table in a copy of the database) and confirm that nothing
     was partially saved and the error is reported.

### 8. (Optional) Move `query_by_month` and `query_by_yearly_table` to `get_connection`

- **Files / functions:** `db_handlers.py`: `query_by_month`, `query_by_yearly_table`. These use the old column
  names (`date`, `charge_name`, `amount`, `tag_id`), so they do not work against the current table either way.
  The only change is the connection handling, plus replacing the f-string `LIKE '{month}%'` with a `?` parameter
  (`(f"{month}%",)`). Do not remove them (no-removals rule).
- **Why do it:** these are the last functions that call `sqlite3.connect` directly, so this keeps
  `db.py` the single owner. Skip it if you would rather leave the dead code untouched, and just keep `import sqlite3`.
- **Verify:** there is no UI path that calls them (`create_query_by_month` is not wired into the app), so a grep
  confirming no live callers is enough.

### 9. Remove the old shared connection

- **Files / functions:** `db_handlers.py`:
  - Delete the `DatabaseSetup` class (class-level `dbconnect` and `write_cursor`, `create_database`,
    `create_budget_table`, `poll_master_table`). By now no live code calls it; grep for `DatabaseSetup` first.
  - Remove `import sqlite3`, and `default_database` if nothing references it any more. Keep `import os` and
    `expenseTable` (used by the new functions and the legacy query defaults).
- **Effect:** importing the app no longer opens or creates `db.sqlite3`. A missing database is only created by the
  Create Database menu action.
- **Known side effect:** `windows/budget_main.py` will fail on its `DatabaseSetup.*` calls (see "not changed" above).
- **Verify:** `grep -rn "sqlite3.connect" budgetbook --include=*.py` shows only `utilities/db.py` (plus the
  `deprecated/` folder). Then run the full checklist in item 10.

### 10. Final regression test and documentation

- **Files:** `CLAUDE.md` (replace the notes about the shared connection and the always-true check with the new
  `db.get_connection` pattern, and remove the bugs this plan fixes), and update this file's status.
- **Full regression with a backed-up database:** Create Database, Create Table, Verify Database, import CSV,
  import PDF, Save, Load Month, Run Report, Delete Duplicates, quit and relaunch.
