# Phase 0 Foundation TODO

This is the foundation work (roadmap Phase 0, see `roadmap.md`): the schema, database layer, backups, importer contract and tests that the later phases build on. Features that sit on top of this (category screens, summaries, budget overlays, the matching logic) are on the roadmap, not here. Where an item below creates a table for a later feature, only the schema is in scope.

Here's what I'd change, roughly in priority order. Nothing is applied yet. (This file was renamed from `TODO-phase1.md` so the name no longer clashes with roadmap Phase 1.)

## Schema

CREATE TABLE accounts (                  -- see item 7
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,  -- display name, e.g. 'Checking 0023'
    account_type  TEXT NOT NULL,         -- 'checking', 'savings', 'credit_card', 'cash', ...
    identifier    TEXT,                  -- bank-provided id (last digits) used to recognize imports
    institution   TEXT,
    is_active     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE);

CREATE TABLE transactions (
    id               INTEGER PRIMARY KEY,
    account_id       INTEGER NOT NULL REFERENCES accounts(id),
    transaction_date TEXT    NOT NULL,   -- ISO 'YYYY-MM-DD'
    post_date        TEXT,               -- ISO or NULL
    name             TEXT    NOT NULL,
    amount_cents     INTEGER NOT NULL,   -- signed, e.g. -1250 = $12.50 charge
    category_id      INTEGER REFERENCES categories(id),
    is_transfer      INTEGER NOT NULL DEFAULT 0,   -- 1 = payment/transfer between accounts, not an expense
    transfer_peer_id INTEGER REFERENCES transactions(id),  -- the matching row in the other account, if imported
    notes            TEXT,
    source           TEXT,               -- 'capone_pdf', 'csv', 'manual'
    import_hash      TEXT UNIQUE,        -- dedupe key, see item 3
    created_at       TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_tx_date ON transactions(transaction_date);
CREATE INDEX idx_tx_account ON transactions(account_id);

CREATE TABLE budgets (                   -- see item 8
    id             INTEGER PRIMARY KEY,
    category_id    INTEGER NOT NULL REFERENCES categories(id),
    amount_cents   INTEGER NOT NULL,     -- positive monthly limit
    effective_from TEXT NOT NULL,        -- 'YYYY-MM', the limit applies from this month on until a newer row replaces it (no rollover)
    UNIQUE (category_id, effective_from)
);

CREATE TABLE merchant_rules (            -- see item 6, created empty in the foundation phase
    id              INTEGER PRIMARY KEY,
    pattern         TEXT NOT NULL,       -- normalized merchant key
    match_type      TEXT NOT NULL DEFAULT 'exact',  -- 'exact' first; 'contains' etc. later without a schema rewrite
    category_id     INTEGER NOT NULL REFERENCES categories(id),
    times_confirmed INTEGER NOT NULL DEFAULT 1,
    UNIQUE (pattern, match_type, category_id)
);

1. Amounts as integer cents.
   - REAL is floating point and drifts on sums. Integer cents are exact, and the Reports tab can sum and group without string cleanup.
   - Format $ and commas only in the display layer, for example in PandasAbstractTable.data(). This also removes the string-stripping in _refresh_report_chart.
   - Pick a sign convention (charges negative or positive) and document it in CLAUDE.md.
2. Dates as ISO text.
   - SQLite has no date type, but ISO text sorts and compares correctly.
   - Use WHERE transaction_date >= '2025-03-01' AND < '2025-04-01' or strftime('%Y', ...) instead of INSTR, which can false-match.
   - Enforce the format with a CHECK (transaction_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]').
3. A real primary key plus a separate dedupe key.
   - id INTEGER PRIMARY KEY is stable, so editing a row's amount updates it instead of creating a duplicate.
   - Put the "have I imported this already" logic in import_hash, computed from account, date, name, amount and the source's own reference if there is one. Include the account so the same purchase imported into two different accounts is not treated as one. Use INSERT ... ON CONFLICT(import_hash) DO NOTHING for imports.
   - Edits from the table view become UPDATE ... WHERE id = ?.
   - Two identical same-day purchases are legitimate. Include an occurrence counter in the hash, or you'll silently drop real transactions. Your current UNIQUE already has this flaw.
4. Tags as a categories table. Free-text tags allows typos ("Grocery" vs "Groceries"), which splits pie slices. A foreign key fixes that and gives the "learn how things get tagged" feature a place to live later, for example a merchant_rules table. If you want multiple tags per transaction, use a join table, but I'd start with single categories.
   - Creating categories without typos: categories are rows the user creates deliberately. The category cell in the table view becomes a dropdown (an editable QComboBox in a QStyledItemDelegate) listing existing categories plus a "New category..." entry, so a category never comes into existence as a side effect of typing in a cell.
   - All creation goes through one function, get_or_create_category(name). It trims whitespace and collapses internal spaces, and matches case-insensitively by declaring the column name TEXT NOT NULL UNIQUE COLLATE NOCASE, so "grocery" and "Grocery" cannot both exist.
   - Near-match check before creating: use difflib.get_close_matches (standard library, no new dependency), including plural/singular. If "Groceries" exists and the user types "Grocery", prompt: "Did you mean Groceries? [Use Groceries] [Create new anyway]".
   - Rename and merge are the long-term fix, since some typos will still get through. Add them to the Admin tab (currently empty) with a category list. Rename is a single UPDATE on one row. Merge repoints category_id on the transactions and deletes the duplicate. With free-text tags, fixing a typo means rewriting every matching row.
   - Keep category_id NULL for uncategorized transactions and let the report join display them as "Other". This removes the blank-to-"Other" fillna step in_refresh_report_chart.
   - Optional: ship a few starter categories (Groceries, Rent, etc.) that the user can rename or delete. Skipped at first since categories should be user-driven.
5. Column names: drop the transaction_ prefix (date, name, amount) if you want it cleaner. That's optional, since renaming touches many files.
6. Learning tags during import. This is separate from creating categories (item 4). It matches incoming transactions to categories automatically, and it depends on the categories table existing, not the reverse, so categories can be built first and rules added later without a schema change to transactions. Scope split: the foundation phase only creates the empty `merchant_rules` table (see Schema). The learning and suggestion logic described in the bullets below is a feature and lives in roadmap Phase 2. `match_type` and room for extra nullable condition columns (such as an amount range) let the later "advanced rules" feature extend the same table instead of adding a second one.
   - Rules table: merchant_rules(pattern TEXT, category_id INTEGER, times_confirmed INTEGER). The pattern is a normalized merchant key: uppercase, with store numbers, dates and trailing location text stripped, so "STARBUCKS #1234 SEATTLE" and "STARBUCKS #88" produce the same key.
   - Learning: each time the user saves a transaction with a category, upsert a rule for its merchant key and bump the count.
   - Import: look up each incoming transaction's key and pre-fill the category when a rule exists. Show these as suggestions (for example a different cell color) that the user confirms by saving. Never commit them silently, because a wrong guess that gets saved is a typo-like error that is hard to find later.
   - Conflicts: if one merchant maps to several categories (Amazon, Walmart), only pre-fill when one category clearly dominates, otherwise leave it blank.
   - Goal not covered, typing a category directly into a cell: the current table cell is plain editable text, which is what causes typos. The dropdown delegate in item 4 needs to replace it.
   - Goal not covered, multiple categories per transaction (for example a Costco trip that is part groceries and part household): a single category_id cannot express this. It needs a join table or a split-transaction feature.
   - Goal not covered, category hierarchy (Food -> Groceries, Restaurants): not in the plan. A nullable parent_id on categories can be added later cheaply, so it does not need deciding now.
   - Design decision: single category or multiple per transaction? Single is simpler and is the recommendation unless split purchases are needed.
   - Design decision: should near-match detection (item 4) prompt the user ("Did you mean Groceries?"), or only autocomplete from existing names?
   - Design decision: should starter categories be shipped, or left empty so categories stay fully user-driven?
7. Accounts and transfers. Every transaction belongs to an account, so a credit card payment that shows up in two imports (as a credit on the card statement and as a debit in checking) can be recognized instead of counted twice.
   - Schema: an `accounts` table and `transactions.account_id` (NOT NULL), plus `is_transfer` and `transfer_peer_id` on transactions (see Schema). Account types cover checking, savings, credit card and cash. Net worth and balance tracking are later roadmap work, but this table is what they will build on, so adding it now avoids a retrofit.
   - Every import is tagged with an account. The import dialog asks which account the file belongs to, and `accounts.identifier` (for example the last four digits) lets an importer pre-select it when the file contains that number. The account is part of `import_hash` (item 3).
   - A transfer is two rows, one per account, linked by `transfer_peer_id`. Reports that total expenses and income leave out rows with `is_transfer = 1`. If only one side was imported (for example only the credit card), the single row is still flagged `is_transfer = 1` with no peer, so it is still excluded from expenses.
   - Detection of pairs (matching logic, a roadmap Phase 2 feature): same absolute amount, opposite signs, different accounts, dates within a few days, and a name that looks like a payment. As with categories, these are suggestions the user confirms, never silent changes. In the foundation phase only the columns are added.
   - Decided: no transaction may exist without an account (`account_id` is NOT NULL). Selecting the account is a standard step of every import. Manual entries also need an account, and the user can create a manual account (for example "Cash") when none fits.
   - Decided: existing rows are not migrated. The current data is test data from developing the importers and CSV parsers, and it will be purged once the new schema and its functionality are validated. Only live data is imported into the live database from then on, so there is no "Unassigned" placeholder account and no conversion of old rows. See the Migration section.
   - A bulk "reassign account" action (by selection or date range) is still wanted as a normal feature (roadmap Phase 1), for fixing a wrongly chosen account on an import.
8. Budgets table. The roadmap's budget-per-category feature needs somewhere to store limits, and the first draft of this file did not have it.
   - `budgets(category_id, amount_cents, effective_from)` stores a monthly spending limit per category. A row means "this category's limit is X from this month onward", so you enter it once and it stays in effect until you change it. A later row for the same category with a newer `effective_from` replaces it from that month on. This only describes how the limit amount is stored.
   - Each month is compared on its own: that month's expenses against that month's limit. There is no rollover. Unspent amounts are never carried into the next month, and no balance is tracked. The unspent-rollover idea is not planned (moved to "Maybe" on the roadmap).
   - Decided: setting or changing a budget takes effect from the current month forward and never rewrites history. The app writes a row with `effective_from` set to the current month and leaves earlier rows alone, so past months keep the limit that was in force then. This keeps the historical budget versus spending picture accurate over time. Editing a past month's limit is a separate, deliberate correction action (not the normal way to change a budget). Reading a month's limit means taking the row with the latest `effective_from` that is not later than that month. A new budget for a category that has none simply starts at the current month.
   - Alternative considered: one row per category per month. It is simpler to query but means entering or copying a row for every month. The "stays in effect until changed" design is recommended.
   - Showing or hiding the budget overlay on the summary is a display option, not data, so it is not in the schema. The summary screens and the overlay are roadmap features.
   - Savings targets are a later idea and would be handled by creating a savings category (possibly with a target amount), not by a rolling balance. Nothing is needed in the schema for that now.
9. Database backup (basic).
   - A `backup_database()` function using SQLite's backup API (`sqlite3.Connection.backup`), which gives a consistent copy even while the app has the file open. It writes a timestamped copy to a backups folder (add that folder to `.gitignore`).
   - It runs automatically before anything destructive: purging the old data, `remove_duplicates`, later bulk edits, and any future schema migration. It is also available as a manual menu action (Database menu now, Admin tab later).
   - Export to CSV and better import and export formats are roadmap features, not part of this item.
   - Design decision: how many backups to keep (for example the last 10, or the last one per day for 30 days).

## Code structure (this is what makes troubleshooting hard)

- One connection owner. Right now there is a module-level connection in settings.py, a class-level one in DatabaseSetup, and a new sqlite3.connect() in nearly every function. Make one small db module with get_connection() as a context manager. Turn on PRAGMA foreign_keys = ON in it, and use with conn: so writes commit or roll back as a unit.
- Parameterized SQL only. remove_duplicates and the legacy queries build SQL with f-strings. The table name is trusted, but values should always go through ? or :name.
- A schema version. Use PRAGMA user_version plus a tiny migration list, so the first schema is version 1 and later changes are numbered migrations rather than "delete the DB and recreate" once real data exists. It also makes the "Create Table" menu actions safe. The first redesign itself is not a migration (existing data is purged, see Migration).
- Dev and live databases. The live database path stays hardcoded for now. Add a simple way to point the app at a separate development database, for example an environment variable (such as `PYBUDGET_DB`) that overrides `settings.expensedb`, so schema work and import experiments never touch live data. This builds on the call-time database path change in Testing item 3, and the same switch is what the tests use for their temporary database. A later user-chosen database prompt replaces both.
- Move DatabaseSetup logic to plain functions that return clear results, such as exceptions or a typed result. Today the tuple-vs-bool mismatch means the Verify Database message is wrong.
- Settings: replace the hardcoded D:\... DB path with a path relative to the package, or a user data directory (platformdirs, which isn't a current dependency).
- A repository layer with functions like insert_transactions(df), get_transactions(year, month) and update_transaction(id, **fields). The GUI then never touches SQL. This also helps your windows/ split, because the windows only call these functions.

## Importers

Keep them as they are, but make the contract explicit. A function that converts a parsed row to (account_id, date_iso, name, amount_cents, ...) and computes the hash in one place would keep the formatting rules out of the GUI and DB code. The importers receive the account (item 7) from the import dialog rather than guessing it.

The PDF importer is still inconsistent. That is a feature reliability task on the roadmap (Phase 1), but it connects here: the importer contract and the stub-based tests (Testing item 5-3) are what will make it possible to fix and keep it fixed.

## Migration

Decided: there is no data migration. The current database holds test data created while developing the importers and CSV parsers, so it will not be converted. The plan is:

1. Build and validate the new schema and functionality against a separate development database (see "Dev and live databases" in Code structure), never against data worth keeping.
2. When it is ready, keep a backup of the old file (`backup_database()`, item 9), purge the live database, create the new schema from scratch at schema version 1, and import only live statements from then on.

No conversion script is written. This also drops the old plan's row-count and per-month-sum comparison. What replaces it is the usual import testing (Testing item 5), plus re-importing a real statement into the new schema as an end-to-end check.

Schema versioning (Code structure) still matters, but for the future: once the live database holds real data, every later schema change needs a numbered, backed-up migration instead of a purge. The first schema version is created fresh.

## Testing with pytest

Reference as "Testing item N" or "Testing item N-M" (item and bullet, same scheme as above). This section is planning only: nothing is created or changed yet. Everything below comes from reading the code, so behaviors marked "confirm" should be verified when the test is actually written.

1. Existing test files. **DONE (2026-10-05):** the old tests were judged not useful and removed so the suite starts fresh. Removed: root `test_main.py` (old `unittest`, only covered `handlers.dateCheck`, had empty `setUp`/`tearDown` and a `1 + 1` placeholder, and one test asserted the opposite of its message), `tests/test_main.py` and `tests/math_operations.py` (tutorial placeholders that could not be collected because of a wrong import). `.gitignore` no longer ignores `tests/` or `test_main.py`, and `.pytest_cache/` is ignored.
2. Setup. **DONE (2026-10-05)** except the planned test files, which are added as each area in item 5 is started.
   - `pytest==9.0.2` is a pinned dev dependency: an optional `dev` group in `pyproject.toml` (`pip install -e .[dev]`) and a line in `requirements.txt` (used by CI).
   - `[tool.pytest.ini_options]` in `pyproject.toml`: `testpaths = ["tests"]`, `pythonpath = ["."]` (so `import budgetbook` works from the repo root even without `pip install -e .`), `addopts = "-ra"`, `xfail_strict = true`, `minversion = "9.0"`. Run from the repo root with `python -m pytest`.
   - `tests/conftest.py` holds the shared setup: keeps pytest's flags away from the logger's `argparse` (`sys.argv` guard), sets `QT_QPA_PLATFORM=offscreen`, creates the untracked `budgetbook/logs/` folder the logger needs, and provides a session-scoped `qapp` fixture. `tests/test_harness.py` has three checks that the framework itself works (package imports, logger ignores pytest flags, Qt runs offscreen).
   - Still planned, one file per area in item 5: `tests/helpers.py`, `test_dates.py`, `test_csv_import.py`, `test_pdf_import.py`, `test_db.py`, `test_table_model.py`, `test_reports.py`.
3. Make the code testable (small prerequisites).
   - Database path at call time: change `get_connection(db_path=None)` to use `db_path or settings.expensedb`, and have `db_handlers` read `settings.expensedb` instead of the import-time `default_database` copy. A fixture can then redirect every database call to a temporary file with `monkeypatch.setattr(settings, "expensedb", ...)`. This changes the default-argument note in `db-connect-schema.md` section 3, so do it with section 8 item 3 or 4 there. Database tests wait for this.
   - Logger and `sys.argv`: `utilities/logger.py` runs `argparse` on `sys.argv` when imported, so pytest's own flags (`-c`, or `--co`, which argparse matches to `--console`) are read as logging options. **Worked around in `tests/conftest.py`** (the `sys.argv` guard, also creating the `budgetbook/logs/` folder the logger needs). The cleaner long-term fix is still to move the `argparse` call into a function that `main()` calls, which would also fix the `-h` crash noted in the README. The logger also appends to the real `runninglog.txt` during tests, which is acceptable at first.
   - Until `DatabaseSetup` is removed (section 8 item 9), importing `db_handlers` opens the real database file as a side effect. Harmless while the file exists, but note it.
4. Fixtures and helpers (`conftest.py`, `helpers.py`).
   - `tmp_db`: points `settings.expensedb` at a fresh file under `tmp_path` and returns the path. `db_with_table`: the same plus `db_handlers.create_budget_table()`.
   - `make_transactions(...)`: builds a DataFrame with the six standard columns from a few readable rows. `write_csv(tmp_path, rows)`: writes a synthetic CSV. All data is synthetic. Real statements are private and gitignored, and must never be committed.
   - `qapp` (session scope): a `QApplication` with `QT_QPA_PLATFORM=offscreen`, only for the few tests that need it (item 5-5 and 5-6 need to confirm whether they do).
5. What to test, by area. The priority rule: test first where a wrong result silently corrupts money data (import parsing, dates, amounts, saving and de-duplicating, report totals), and keep the GUI layer thin.
   - 5-1 Date handling (`handlers.dateCheck`, `FileImportHandlers.date_check`, `format_date`, `format_import_dataframe`).
     - Run the same input matrix through both validators: valid ISO, `"Mar 05"`, garbage text, empty string, `None`, an integer, and the `fuzzy` flag. They differ: `dateCheck` catches `ValueError` and `TypeError`, while `date_check` only catches dateutil's `ParserError`, so `None` or an integer probably raises. Confirm, then decide whether to consolidate them into one function.
     - `parse_csv` decides whether a cell is a date by calling `date_check` first, and `dateutil` is permissive. Feed it realistic cells (a bare number, a lone month word, a merchant name containing digits, amounts with and without `$`) to find out what gets misclassified as a date. This is a characterization test: record today's behavior, then decide if it is acceptable.
     - `format_date` expects `"Mon DD"` plus a year **string** (it concatenates them), so an integer year raises `TypeError` even though `importer_csv` defaults to `year: int = 2025` and the type hints say int. Test the string case, the int case (probably an expected-failure test), invalid dates such as Feb 29 in a non-leap year (uncaught `ValueError`), and note that `%b` depends on the system locale.
     - Year boundary: one import year is applied to every row, so a December statement that includes early-January transactions gets those January dates in the wrong year. Decide the intended rule (for example, roll the year forward when the month is earlier than the statement month) and write the test for it.
     - `format_import_dataframe`: converts both date columns, keeps the row count, mutates the input frame in place, and one bad date aborts the whole import. Test each.
   - 5-2 CSV import (`parse_csv`, `importer_csv`, `handlers.import_file_dialogue`).
     - `parse_csv` builds its list in the order it finds things, so the row's shape decides the columns. A normal row (two dates, a name, a `$` amount) gives six values: date, post date, name, amount, empty tag, empty note. Test that, plus a row with one date, a header row, blank cells, extra columns, negative amounts, and thousands separators (`"$1,234.50"`). Rows that do not produce six values make the `DataFrame(...)` call in `importer_csv` fail or misalign, so record what happens.
     - Amounts stay text today (`"4.50"`, `"-4,500.00"`). That is the current contract, and it is where the future integer-cents conversion (item 1) gets its tests.
     - `importer_csv`: a missing file returns `None` (callers do not check it), blank lines are skipped, and the column names match the table.
     - `import_file_dialogue` picks the importer with `str(name).split(".")[1]`, which takes the second dot-separated piece. A dot in a folder name or a name like `statement.2025.csv` can select the wrong importer or none, `"csv" in file_type` is case sensitive (`.CSV` does not match), and the file dialog also offers `.xls`/`.xlsx`, which fall through and return `None`, which then flows into `update_table_from_dataframe`. Test the dispatch with the importers replaced by a fake object that records calls, so no files are needed.
   - 5-3 PDF import (`Page`, `cap_one_import`). Test in layers because a real PDF is the hardest thing to build.
     - `Page.parse_transaction_table` with a small stub page object (no PDF): 4 columns are renamed, 5 columns are renamed, any other count gives an empty frame, blank strings become NaN and those rows are dropped. When no table is found it returns the string `""` rather than a DataFrame, while callers use `.empty`, so that case likely raises `AttributeError`. Confirm.
     - `find_table_end`, `find_transaction_table`, `get_rect` with a stub whose `search_for` returns rect-like objects: the clip bottom is the rounded `y1` minus 5, and a missing needle keeps the previous value.
     - `cap_one_import` mixes reading the PDF with all the cleanup, so today it can only be tested end to end. Recommended small, behavior-preserving refactor: extract the DataFrame cleanup (concatenate pages, drop rows with no date, merge the split date columns, repair the trailing minus sign, format dates) into a pure function that takes synthetic frames. Edge cases to cover: no tables found (`pd.concat` of an empty list raises), a single-row result (the spot check reads `iloc[1]`), both column layouts (the variable `row_check_merge_required` reads inverted compared with its comment), and an amount whose minus sign ended up at the end of the name column (`"- " + amount`).
     - End to end: opt-in only. Skip unless an environment variable (for example `PYBUDGET_SAMPLE_PDF`) points to a local statement, then compare row count and total. Generating a fake PDF with `pymupdf` is possible but fragile because table detection depends on layout, so it is low priority.
   - 5-4 Database layer (`db.py`, `db_handlers`). Use a real temporary SQLite file, not mocks.
     - `get_connection`: commits on success, rolls back and re-raises on an exception, closes the connection, and turns on `foreign_keys`.
     - `table_exists` (no file gives False and does not create the file; file without the table; file with the table), `create_database` and `create_budget_table` (created once, then report "already exists"). This automates the manual checklist in `db-connect-schema.md` section 8 item 4.
     - `save_dataframe_to_db`: rows are inserted; saving the same data again adds no rows; changing tags or notes updates the existing row; column order in the DataFrame does not matter; `NaN` or `None` in tags or notes; a failure rolls the whole batch back (after section 8 item 7). Known flaw to pin: two genuinely identical same-day purchases collapse into one row because of the `UNIQUE` key. Write it as an expected-failure test that the `import_hash` design (item 3) must turn green.
     - `load_db_to_dataframe`: year only, month plus year, "All" and "Whole Year", an empty result, and boundaries for the `INSTR` match (a month filter must not match a day number; this becomes a date-range query in item 2).
     - `remove_duplicates`: keeps the lowest `rowid`, running it twice removes nothing the second time, and returns a count (after section 8 item 6).
   - 5-5 Table model (`PandasAbstractTable`). Probably no `QApplication` needed (confirm).
     - `rowCount`/`columnCount`, `data()` (note it returns `str(value)` for every cell, so numbers become text, which matters for sorting and for the display-formatting plan in item 1), an invalid index returns `None`, `headerData` (horizontal uses the display headers, vertical uses the index labels).
     - Editing: `setData` writes into the DataFrame in place and returns `True`, a non-edit role returns `False`, and `dataChanged` is emitted. `flags` includes editable. `update_table_from_dataframe` swaps the data and emits a model reset. Capture the signals with a simple slot that appends to a list.
     - Constructing it without `display_headers` falls back to `self.data.columns`, but `self.data` is the `data()` method, not the DataFrame, so this likely raises `AttributeError`. Write it as an expected failure. Also test `display_headers` shorter than the column count (`IndexError` in `headerData`).
   - 5-6 Report totals and the pie series.
     - The pandas logic inside `MainWindow._refresh_report_chart` (strip spaces, `$` and commas, cast to float, blank tags become "Other", group and sum) cannot be tested without building the window. Recommended small refactor: extract it into a pure function such as `summarize_by_tag(df) -> dict`, then test: currency stripping, blank and `NaN` tags, sums per tag, an empty frame, negative amounts (depends on the sign convention in item 1-3). After the integer-cents change the cleanup disappears and these tests get simpler.
     - `QtPieChartSeries`: slice count and values match the dict, an empty dict works, negative values. Its label uses only the first word of the category, so `"Grocery Store"` and `"Grocery Other"` both show as "Grocery". Decide whether that is intended. Do not assert on colors, or replace `random_color_gen` with a fixed value. Confirm whether it needs a `QApplication`.
   - 5-7 Small utilities: `random_color_gen` returns `#` plus six hex digits (replace `random.randint` with a fixed function for a deterministic check).
   - 5-8 New design, written as tests first (they act as the specification): amount text to integer cents, ISO date normalization, `import_hash` including the occurrence counter, `get_or_create_category` (trimming, case-insensitive match, near-match prompt), merchant key normalization and rule lookup (item 6), and the new schema itself (created at version 1 with the expected tables, foreign keys enforced, hashes unique). There is no data migration to test (see the Migration section).
   - 5-9 Not worth unit tests now: window and menu construction (`MainWindow.__init__`), dialog layout in `gui_handlers`, `logger.py`, the standalone tools (`capone2csv_standalone.py`, `import_template_tool.py`). If wanted later, one smoke test that creates `MainWindow` offscreen and checks the tab titles is enough.
6. How to test (principles).
   - Work in layers from cheapest to most expensive: pure functions (no fixtures), synthetic DataFrames, a temporary SQLite file, Qt models without a window, and last an optional GUI smoke test.
   - Two kinds of tests. Characterization tests pin what the code does today so a refactor cannot change it silently. Specification tests describe the desired behavior for things that are known to be wrong. For known bugs use `pytest.mark.xfail(strict=True, reason="see TODO Testing item 5-x")`: the suite stays green, and when the bug is fixed the test turns into a failure that tells you to remove the marker.
   - Prefer real SQLite and real DataFrames. Use mocks or stubs only for the file dialog dispatch (5-2) and the PDF page objects (5-3).
   - One behavior per test, with `pytest.mark.parametrize` for input tables. Do not assert on `print` output or log text.
   - Synthetic data only, built with the helpers in item 4.
7. Suggested order of implementation (each step is small and can be run on its own).
   1. Setup (item 2), the `sys.argv` handling in `conftest.py` (item 3), and a first test file for `random_color_gen` and the date validators (5-7, 5-1). This proves the harness works and replaces the old unittest.
   2. `format_date`, `format_import_dataframe`, `parse_csv`, `importer_csv` (5-1, 5-2).
   3. Table model (5-5).
   4. The call-time database path change (item 3), the `tmp_db` fixture, then the database tests (5-4) alongside section 8 items 4 to 7 of `db-connect-schema.md`, so each moved function gets its test first.
   5. Extract `summarize_by_tag` and test it, then the pie series (5-6).
   6. PDF layers (5-3), starting with the stub-based tests, then the cleanup refactor.
   7. Specification tests for the new schema and importer contract (5-8) as that work starts.
8. Running and CI.
   - All: `python -m pytest`. One file: `python -m pytest tests/test_db.py`. One test: `python -m pytest -k save_dataframe`.
   - CI: `.github/workflows/pylint.yml` only runs pylint. Add a pytest step once the tests are stable. It installs from `requirements.txt`, and no test may depend on the `D:\` path (item 3 handles that).
   - Optional: `pytest-cov` for coverage (`htmlcov/` and `.coverage` are already ignored).
9. Design decisions to make.
   - Consolidate `dateCheck` and `date_check` into one validator (5-1).
   - Intended year-boundary rule for imports (5-1) and whether `format_date` should accept an integer year.
   - Whether to fix the logger's `argparse` at the source or work around it in `conftest.py` (item 3).
   - Allow the small refactors in 5-3 (extract the cleanup function) and 5-6 (extract `summarize_by_tag`), or limit tests to what the current structure allows.
   - Where the `pytest` dependency lives (item 2), and whether to add `pytest-qt` later.

## Suggested order

1. Add the single connection module and parameterize the queries. This has the lowest risk and the biggest debugging benefit. (Detailed steps: `db-connect-schema.md` section 8.)
2. Add `backup_database()` (item 9) so everything after this step can be undone.
3. Add schema versioning.
4. Design the new schema (all tables in the Schema section, including accounts, budgets and the empty merchant_rules) as a version 1 create-from-scratch function, and verify it on a separate development database. No data migration (see Migration).
5. Switch the repository functions and the GUI to the new columns, with an account chosen at import.
6. Test setup is already in place. Add tests for each area as it is touched (see "Testing with pytest").
