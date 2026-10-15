#!/usr/bin/python
"""This file is a universal location for common variables within the application landscape.
Eventually I want this to move to something more robust like the database itself."""
import os

expensedb = os.path.join("D:\\", "scripts", "pybudget", "budgetbook", "db.sqlite3")
expenseTable = "transactions"


def get_db_path() -> str:
    """Database path resolved at call time: the PYBUDGET_DB environment variable (a separate
    development or test database) wins, otherwise the live path in expensedb."""
    return os.environ.get("PYBUDGET_DB") or expensedb


month_dict = {
    "Jan": "January",
    "Feb": "February",
    "Mar": "March",
    "Apr": "April",
    "May": "May",
    "Jun": "June",
    "Jul": "July",
    "Aug": "August",
    "Sep": "September",
    "Oct": "October",
    "Nov": "November",
    "Dec": "December",
}

year_list = ["2026", "2025", "2024", "2023", "2022", "2021", "2020"]
if __name__ == "__main__":
    print("I am a settings file, why did you run me?  LOL")
