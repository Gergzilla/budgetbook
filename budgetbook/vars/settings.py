#!/usr/bin/python
import os
import sqlite3

# mydb = os.path.join(os.path.dirname(__file__), "", "data", "mybudget.db")
mydb = os.path.join("D:\\", "scripts", "pybudget", "budgetbook", "db.sqlite3")
expenseDB = os.path.join("D:\\", "scripts", "pybudget", "budgetbook", "db.sqlite3")
dbconnect = sqlite3.connect(expenseDB)
# mytable = "database_transaction"
expenseTable = "transactions"

month_selector = {
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

if __name__ == "__main__":
    print("I am a settings file, why did you run me?  LOL")
