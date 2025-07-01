#!/usr/bin/python
# This file is a copy of db_handlers.py but is being modified for django integration and testing
import sqlite3
import os
import pandas as pd
from vars import settings

from utilities.logger import LoggingHandler

# try:
#     from utilities.logger import LoggingHandler
# except Exception:
#     from logger import LoggingHandler

#### Database Setup Functions #####
default_database = settings.expenseDB
expenseTable = settings.expenseTable
logger = LoggingHandler("db_handlers").log  # currently untested


class DatabaseSetup(object):
    """my doc is my string, verify me"""

    def __init__(self):
        self.name = __name__
        self.logger = LoggingHandler(__class__).log
        pass

    def __str__(self):
        return self.name

    @staticmethod
    def create_database(live_expense_database: str = default_database):
        """my doc is my string, verify me"""
        # can prompt for db name in the future, for now its hard set
        if os.path.exists(live_expense_database):
            # print("File exists, establishing connection to " + expenseDB)
            dbconnect = sqlite3.connect(live_expense_database)
        else:
            print("Database File doesnt exist, creating file")
            logger.info("Database File doesnt exist, creating file")
            try:
                dbconnect = sqlite3.connect(live_expense_database)
            except Exception:
                print(
                    "could not create file for some reason at " + live_expense_database
                )
                logger.info(
                    "could not create file for some reason at " + live_expense_database
                )
                dbconnect = ""
        return dbconnect

    @staticmethod
    def create_budget_table(live_expense_database: str = default_database) -> str:
        """my doc is my string, verify me"""
        # create expenses table if it doesnt exist
        # this is disabled for now due to django integration
        dbconn = sqlite3.connect(live_expense_database)
        write_cursor = dbconn.cursor()
        table_check = DatabaseSetup.poll_master_table(write_cursor)
        print(table_check)
        if table_check is False:
            print("Table check is False, meaning table needs to be made")
            # print("do nothing")
            write_cursor.executescript(
                "CREATE TABLE transactions ('Transaction Date' TEXT, 'Post Date' TEXT, "
                "'Charge Name' TEXT, 'Charge Amount' REAL, Tags TEXT, Notes TEXT, "
                "UNIQUE('Transaction Date','Charge Name','Charge Amount'))"
            )
            dbconn.commit()
            if DatabaseSetup.poll_master_table:
                print("Table created")
            else:
                print("table still not found - something broke")
        else:
            print("Table check passed, nothing to do")
            return

    @staticmethod
    def poll_master_table(cur):
        """my doc is my string, verify me"""
        masterdblist = cur.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name='transactions'"
        )
        try:
            checktables = masterdblist.fetchone()
        except Exception:
            checktables = None
        if checktables is None:
            return False
        else:
            return True


##### Data add/remove functions  ######


def save_dataframe_to_db(input_frame: pd.DataFrame) -> None:
    # THIS IS THE LIVE AND WORKING ONE
    """
    This should parse an input dataframe and save it to the sqlite3 database
    """
    dbconn = sqlite3.connect(default_database)
    write_cursor = dbconn.cursor()
    for index, row in input_frame.iterrows():
        transaction_data = [
            row["Transaction Date"],
            row["Post Date"],
            row["Charge Name"],
            row["Charge Amount"],
            row["Tags"],
            row["Notes"],
        ]
        # this does create new entries without duplicates and allows for updates but if there are
        # conflicts and data is empty it could overwrite for example if you import the same file
        # and chang enothing and save, it wont create duplicates but any unprotected fields: aka
        # post_date, tags, notes in the new conflicting data can overwrite/NULL the data
        # already in the DB
        write_cursor.execute(
            "INSERT INTO transactions ('Transaction Date', 'Post Date', 'Charge Name',"
            " 'Charge Amount', Tags, Notes)"
            " VALUES (?,?,?,?,?,?) "
            'ON CONFLICT ("Transaction Date","Charge Name","Charge Amount") '
            "DO UPDATE SET 'Transaction Date' = excluded.'Transaction Date', 'Post Date' = "
            "excluded.'Post Date', 'Charge Name' = excluded.'Charge Name', "
            "'Charge Amount' = excluded.'Charge Amount', Tags = excluded.Tags, "
            "Notes = excluded.Notes",
            transaction_data,
        )

    dbconn.commit()
    # write_cursor.execute(
    #     "SELECT rowid, * FROM transactions WHERE charge_name IS NOT NULL"
    # )
    # rowlist = write_cursor.fetchall()
    # for row in rowlist:
    #     print(row)


def write_to_expenses(writedata="", live_expense_database=default_database):
    """my doc is my string, verify me"""
    dbconn = sqlite3.connect(live_expense_database)
    writeCursor = dbconn.cursor()
    try:
        writeCursor.execute(writedata)
        dbconn.commit()
    except Exception as e:
        print("Error executing query: ", e)
    writeCursor.close()


# these last two functions need to be refactored because they are using the wrong SQL formatting
# AND need to update with hardcoded table name
def add_expenses(expensedata, expenses_table="transactions"):
    """my doc is my string, verify me"""
    # this is the proper format for insertion and works to auto increment ROWID
    # otherwise you can get a 'table has x columns but y supplied' unless you specificy the ROWID
    # as well which isnt needed

    insertString = (
        "INSERT INTO {0} (charge_date, charge_name,"
        " amount, tag_id, notes) VALUES ({1})".format(expenses_table, expensedata)
    )  # bad form, but used to work. changing to placeholders
    print(insertString)
    write_to_expenses(insertString)


def add_tags(expensdata, tag, expenses_table="transactions"):
    """my doc is my string, verify me"""
    # more learning, the for loop for a tuple doesnt work on a single item because there is
    # nothing to iterate over so here it is just a,b,c,y,z = tuple
    date, entity, charge, activetag, note = expensdata
    if activetag and note:
        # activetag and note not needed here but allocated anyways to prevent ValueError
        print(f"{activetag} - {note}")

    tagUpdate = (
        "UPDATE {0} SET tag='{1}' WHERE date='{2}' AND charge_name='{3}' AND"
        " amount={4}".format(expenses_table, tag, date, entity, charge)
    )
    result = write_to_expenses(tagUpdate)
    return result


##### read-only database functions  ########


def queryByMonth(
    month,
    year="2024",
    live_expense_database=default_database,
    expenses_table=expenseTable,
):
    """my doc is my string, verify me"""
    dbconn = sqlite3.connect(live_expense_database)
    readCursor = dbconn.cursor()
    monthQuery = (
        "SELECT date, charge_name, amount, tag_id, notes FROM {0} WHERE "
        "date LIKE '{1}%'".format(expenses_table, month)
    )
    try:
        readCursor.execute(monthQuery)
        monthlyExpenses = readCursor.fetchall()
    except Exception as e:
        print("Unable to execute for for reason: ", e)
        monthlyExpenses = e
    readCursor.close()
    return monthlyExpenses


def queryByYearlyTable(
    expenses_table=expenseTable, year="2024", live_expense_database=default_database
):
    """my doc is my string, verify me"""
    dbconn = sqlite3.connect(live_expense_database)
    readCursor = dbconn.cursor()
    # Specify exact columns so you always know what you are getting back and dont get
    # 'too many values' errors
    recordquery = "SELECT date, charge_name, amount, tag_id, notes FROM {0}".format(
        expenses_table
    )
    # print(recordquery)
    try:
        readCursor.execute(recordquery)
        fulltable = readCursor.fetchall()
    except Exception as e:
        print("unable to execute query for reason: ", repr(e))
        fulltable = e
    readCursor.close()
    return fulltable


##### maintenance functions ######


def removeDuplicates(
    expenseDB=default_database, expenseTable=expenseTable, year="2024"
):  # Not currently used
    """my doc is my string, verify me"""
    dbconn = sqlite3.connect(expenseDB)
    writeCursor = dbconn.cursor()
    rowquery = (
        "SELECT MIN(rowid) FROM {0} group by charge_date, charge_name, amount".format(
            expenseTable
        )
    )
    print(rowquery)
    deletedupes = "DELETE FROM {0} WHERE rowid not in({1})".format(
        expenseTable, rowquery
    )
    print(deletedupes)
    removalResult = writeCursor.execute(deletedupes)
    print(removalResult)
    dbconn.commit()
    writeCursor.close()


if __name__ == "__main__":

    print(
        "I'm a library of database functions.  I dont think you meant to run this directly."
    )
