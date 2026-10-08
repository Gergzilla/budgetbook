# Budget Book Roadmap (draft)

**Product Vision:** A local, private budgeting and expense tracking application that turns imported bank and credit card statements into clear category summaries, built with the goal of expanded functionality over current personal budget tracking.  Also to avoid a lot of nonsense in current public budget tracking offerings around broken features and privacy.

**Audience:** I am my initial target audience with others being the second as a bonus. Priorities wise anything that only matters for public release (accounts and logins, sharing, onboarding) is much lower in priority adn phases or even only in the "Maybe" list.

**Document status:** Heavily rewritten on 2026-10-06 from the original roadmap which frankly was pretty hastily crammed together. Phases are now ordered by dependency, not by calendar months. Status values: **Done**, **Partial**, **In progress**, **Not started**. The detailed Phase 0 Foundation plan is in [`TODO-foundation.md`](TODO-foundation.md).

## Principles

- Personal use comes first. Public-friendly decisions are only made when they align well with the personal use goals or cost little (one importer per bank, data stays local).
- Data correctness before features: amounts, dates and duplicates must be right and consistent imports before summaries are trusted.
- Anything automatic (categories, transfer matching) is a suggestion the user confirms, never a silent change.
- Credit card payments and transfers between accounts are not expenses and must never be double counted and should be simple to tag as such.

## Core important features that shape the goals

1. Assigning a category to imported transactions (for example a business name).
2. Month view: all expenses broken down by category.
3. Year view: each category compared month to month, to spot unusually high months.
4. Budgets per category, shown on the summary only when wanted (secondary).
5. Useful report options for the above and others to make it easy to compare historical datasets.

---

## Phase 0: Foundation

**Goal:** A reliable data layer that the later phases build on. Mostly invisible to the user. Details and open decisions are in `TODO-foundation.md`.

- **Database connection layer** (Critical)
  - One module owns all connections (context manager that commits, rolls back and closes).
  - **Status:** In progress. The new `db.py` module and the new table/database validation functions exist. The menu handlers, load, save and duplicate removal still use the old code (`db-connect-schema.md`, section 8, items 4 to 10).
- **Schema redesign** (Critical)
  - Dates as ISO text, amounts as integer cents, a real primary key plus an `import_hash` for de-duplication, a `categories` table, an `accounts` table with `account_id`, transfer flags, and the `budgets` and `merchant_rules` tables created ahead of the features that use them. The current database is test data and is not migrated: once the new schema is validated (on a separate development database), the live database is backed up, purged and created fresh, and only live statements are imported from then on.
  - **Status:** Planned, nothing applied (`TODO-foundation.md` items 1 to 8 and the Migration section).
- **Account-tagged imports and transfer groundwork** (High)
  - Every transaction belongs to an account, so a card payment seen in two imports can be recognized later. Choosing the account is a standard step of every import, and a manual account (for example "Cash") can be created when none fits. This phase only adds the columns and the account choice at import.
  - **Status:** Not started (`TODO-foundation.md` item 7).
- **Database backup (basic)** (High)
  - A backup function using SQLite's backup API, run automatically before purging the old data and other destructive actions, plus a manual menu action.
  - **Status:** Not started (`TODO-foundation.md` item 9).
- **Importer contract** (High)
  - One clear function that turns a parsed row into the standard fields and the import hash, with the account supplied by the import dialog.
  - **Status:** Not started.
- **Automated tests (pytest)** (High)
  - **Status:** Framework done (config, shared setup, harness check). Tests for dates, imports, database, table model and reports are added area by area as that code is touched (`TODO-foundation.md`, "Testing with pytest").
- **GUI structure refactor** (Medium)
  - Split the window code out of `__main__.py` into the `windows/` package. The structure is not decided yet, so nothing changes until it is.
  - **Status:** Not started (a duplicate `windows/budget_main.py` exists but is not wired in).

---

## Phase 1: Core Personal Use

**Goal:** Everything needed to replace the Google Sheet for day to day use: import, categorize, and view the month and year summaries.

- **Categories** (Critical)
  - Create categories deliberately (dropdown with a "New category" entry), guard against typos and near-duplicates, rename and merge in the Admin tab, show uncategorized transactions as "Uncategorized".
  - **Status:** Partial. A free-text `tags` column is editable in the table, with no category list and no typo protection. The schema groundwork is in Phase 0.
- **Import with account selection** (Critical)
  - CSV and Capital One PDF import into the new schema, choosing the account for each file.
  - **Status:** Partial. CSV import works and Capital One PDF import works but is inconsistent with recent statement changes. Stabilizing the PDF importer (using the stub-based tests planned for it) is part of this item. Other institutions are Phase 2.
- **Expense summary by category** (Critical)
  - Month view: expenses by category. Year view: a category by month grid for month to month comparison. Transfers and payments are excluded.
  - **Status:** Partial. A pie chart of totals by tag for one month or year exists on the Reports tab. The year-by-month comparison does not exist, and the Summary tab is a stub.
- **Transfers and payments excluded from expenses** (High)
  - A manual way to mark a transaction as a payment or transfer, and reports that leave those out. Automatic suggestions come in Phase 2.
  - **Status:** Not started (depends on the Phase 0 schema).
- **Transaction list and filtering** (High)
  - Filter by account, category, date range, and search notes.
  - **Status:** Partial. Loading by month and year works on the Data tab, with no other filters.
- **Manual transaction entry** (High, was Critical)
  - Add and correct transactions by hand, for cash and fixes.
  - **Status:** Not working. Entering rows without an import fails, so a basic "add row" is needed.
- **Bulk reassign account** (Medium)
  - Move a selection or a date range of transactions to a different account, for fixing a wrong account choice on an import.
  - **Status:** Not started (depends on the Phase 0 schema).
- **Export and basic backup access** (High)
  - Export transactions and summaries to CSV, and a menu action for the Phase 0 backup.
  - **Status:** Not started.
- **CSV cleanup utility** (side project, current focus)
  - A standalone tool (`windows/csv_util.py`) that cleans CSV files into the format used by the original Google Sheet. It runs independently of the main app.
  - **Status:** In progress, with known bugs in the open-file handler.

---

## Phase 2: Automation and Insight

**Goal:** Less manual work, and the budget comparison.

- **Category learning during import** (High)
  - Suggest categories from past choices using the `merchant_rules` table, shown as suggestions the user confirms. Phase 0 only creates the empty table.
  - **Status:** Not started.
- **Transfer and payment matching** (High)
  - Suggest pairs across accounts (same amount, opposite signs, close dates, payment-like names) for the user to confirm.
  - **Status:** Not started.
- **Budgets per category with a summary overlay** (High)
  - Set a monthly limit per category and optionally overlay it on the monthly summary. Each month is compared on its own (that month's expenses against that month's limit), with no rollover of unspent amounts.
  - Setting or changing a limit applies from the current month forward and never rewrites past months, so the history of budget versus spending stays accurate. Updating a past month is a separate, deliberate action.
  - **Status:** Not started. The `budgets` table is a Phase 0 schema item.
- **More import formats** (Medium)
  - Additional institutions through the existing template tool, plus better CSV and PDF handling.
  - **Status:** Partial. A PDF template tool exists. Only Capital One has a PDF parser.
- **Richer reports** (Medium)
  - Bar and trend charts, category over time. The basic pie chart and the year-by-month grid are Phase 1.
  - **Status:** Not started.

---

## Phase 3: Planning Tools

**Goal:** Looking forward, once the data is trustworthy. Lower priority because the developer imports actuals rather than planning ahead.

- **Recurring transactions** (Medium)
- **Forecasting and what-if scenarios** (Medium, depends on recurring)
- **Savings targets** (Medium): handled by creating a savings category, possibly with a target amount similar to being a budget, the category will already exist but the savings and goal focused features are exclusive to this phase.
- **Advanced transaction rules** (Medium): an extension of `merchant_rules` (for example "contains Starbucks and amount under $10"), not a second system.
- **Custom dashboards** (Medium)
- **Notifications and alerts** (Low)
- **Custom reports** (Medium)
- **Status for all of the above:** Not started.

---

## Later

Wanted eventually, but not soon.

- **Net worth and balances** (assets, liabilities): builds on the `accounts` table.
- **Bank account integration** (Plaid or similar): low priority and possibly never, because of cost and each bank's quirks. More import formats is the realistic alternative.
- **Investment tracking** and **debt payoff planning**.
- **Data protection** (encrypting the database or a login) before the application is officialy released for public use outside of a Beta.

## Maybe (not planned)

Moved out of the main plan because they do not serve the developer's own use. They can return if the app is released publicly.

- Budget rollover (carrying unspent amounts into the next month): not wanted for now, each month stands alone
- User onboarding and account creation (sign-up, profiles)
- Shared budgets (couples, roommates), this can loosely be handled via accounts on import but multi-user support needed for anything beyond
- Financial learning resources
- Receipt scanning and OCR
- Credit score tracking
- Gamification and rewards

---

## Dependencies at a glance

| Feature | Needs first |
| --- | --- |
| Categories (Phase 1) | Phase 0 schema (`categories` table, cents, ISO dates) |
| Category summaries (Phase 1) | Categories, cents, transfers excluded |
| Transfers excluded (Phase 1) | `accounts`, `account_id` and transfer flags (Phase 0) |
| Category learning (Phase 2) | Categories, `merchant_rules` table (Phase 0) |
| Transfer matching (Phase 2) | `accounts`, transfer flags |
| Budgets overlay (Phase 2) | Categories, `budgets` table, category summaries |
| Savings targets, forecasting (Phase 3) | Categories, budgets, recurring transactions |
| Net worth (Later) | `accounts`, balances |

## Open questions

- What exactly makes the PDF import inconsistent (page layout changes, column counts, trailing minus signs)? The stub-based importer tests should help find it.
- Backup retention: how many backups to keep.
- How to switch between a development database and the live one (an environment variable override is proposed in `TODO-foundation.md`, Code structure).
