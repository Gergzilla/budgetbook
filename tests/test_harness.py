"""Checks that the test framework itself is set up correctly.  These test none of the app logic."""


def test_package_is_importable():
    import budgetbook

    assert budgetbook.__file__


def test_logger_ignores_pytest_flags():
    from budgetbook.utilities import logger

    # defaults, which means the argv guard in conftest.py kept pytest's flags away from argparse
    assert logger.options.log == "warning"
    assert logger.options.console == "false"


def test_qt_runs_offscreen(qapp):
    assert qapp.platformName() == "offscreen"
