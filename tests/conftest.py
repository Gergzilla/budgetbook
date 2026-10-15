"""Shared pytest setup for the budgetbook test suite.

Pytest loads this file before any test module, so the process-wide workarounds below run before
anything imports budgetbook.  Fixtures shared by several test files also live here.
"""

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

import pytest

# utilities/logger.py runs argparse on sys.argv when it is imported.  Without this, pytest's own
# command line flags (for example -c, or --co which argparse abbreviates to --console) would be
# read as the application's logging options.  Keep only the program name.
sys.argv = sys.argv[:1]

# Qt must not open real windows during tests.  setdefault lets a developer override it.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Importing db_handlers still opens the database at settings.get_db_path() (DatabaseSetup, until it
# is removed).  Point the whole session at a throwaway file so a test run can never touch the live
# database.  Individual tests use the tmp_db fixture below for their own file.
os.environ["PYBUDGET_DB"] = os.path.join(
    tempfile.mkdtemp(prefix="pybudget-session-"), "session.sqlite3"
)

# logger.py appends to budgetbook/logs/runninglog.txt at import.  That folder is not tracked by
# git, so a fresh checkout (or CI) would fail on import without it.
_package = importlib.util.find_spec("budgetbook")
if _package is not None and _package.origin:
    (Path(_package.origin).parent / "logs").mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def qapp():
    """One QApplication for the whole test session, for tests that create Qt widgets."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """A fresh database at the current schema version, selected through PYBUDGET_DB.
    Returns its path."""
    from budgetbook.utilities import schema

    path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("PYBUDGET_DB", str(path))
    schema.migrate()
    return path
