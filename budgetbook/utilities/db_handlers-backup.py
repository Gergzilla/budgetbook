#!/usr/bin/python
"""This module is handler functions and classes related to interacting with the SQLite database"""

"""I am a backup of the db_handlers prior to refactoring the db in order to remove the spaces in the table names
and other aggressive cleanup like tweaking column formating.  Howefully I wont be needed but with the scope of the 
changes to be made a full file backup was necessary"""
import sqlite3
import os
from datetime import datetime
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


class DatabaseSetup:
    """This is the initial database and table setup, It has been setup within the Database menu of the app
    Some tweaking is still needed for better user feedback and error handling
    But for now they are just collected together in a proper method class"""

    live_expense_database = default_database
    # hard set for now from settings file. I will figure out dynamic later when I make a full DB menu
    try:
        dbconnect = sqlite3.connect(live_expense_database)
    except Exception as e:  # yes its generic, not sure what I might get here yet.
        print("throwing a generic exception for now for visibility")
        print({e})

    write_cursor = dbconnect.cursor()

    def __init__(self):
        self.name = __name__
        self.logger = LoggingHandler(__class__).log

    def __str__(self):
        return self.name

    @staticmethod
    def create_database():
        """my doc is my string, verify me"""
        # can prompt for db name in the future, for now its hard set
        if os.path.exists(DatabaseSetup.live_expense_database):
            # print("File exists, establishing connection to " + expenseDB)
            dbconnect = sqlite3.connect(DatabaseSetup.live_expense_database)
            return True
        else:
            print("Database File doesnt exist, creating file")
            logger.info("Database File doesnt exist, creating file")
            try:
                sqlite3.connect(DatabaseSetup.live_expense_database)
                # dbconnect = sqlite3.connect(DatabaseSetup.live_expense_database)
                return True
            except RuntimeError:
                # Might need to tweak the exception type
                print(
                    "could not create file for some reason at "
                    + DatabaseSetup.live_expense_database
                )
                logger.info(
                    "could not create file for some reason at "
                    + DatabaseSetup.live_expense_database
                )
                return False

    @staticmethod
    def create_budget_table() -> str:
        """my doc is my string, verify me"""
        # create expenses table if it doesnt exist
        table_check, status = DatabaseSetup.poll_master_table()
        # print(table_check)
        if table_check is False:
            print("Table check is False, meaning table needs to be made")
            logger.error("Master Table check is False, meaning table needs to be made")
            # this should be wrapped in a try/except loop
            DatabaseSetup.write_cursor.executescript(
                "CREATE TABLE transactions ('Transaction Date' TEXT, 'Post Date' TEXT, "
                "'Charge Name' TEXT, 'Charge Amount' REAL, Tags TEXT, Notes TEXT, "
                "UNIQUE('Transaction Date','Charge Name','Charge Amount'))"
            )
            # DatabaseSetup.write_cursor.executescript(
            #     "CREATE TABLE transactions ('Transaction Date' TEXT, 'Post Date' TEXT, "
            #     "'Charge Name' TEXT, 'Charge Amount' REAL, Tags TEXT, Notes TEXT, "
            #     "UNIQUE('Transaction Date','Charge Name','Charge Amount'))"
            # )  #the old db, fixing column names again
            DatabaseSetup.dbconnect.commit()
            if table_check:
                # this internal if makes no sense, it would never be hit because if has to be false first
                # and then somehow be true
                logger.info("Table created")
                return (True, "Table created")
            else:
                logger.critical(
                    "Table could not be created, check log messages for more details."
                )
                return (
                    False,
                    "Table could not be created, check log messages for more details.",
                )
        else:
            # print("Table check passed, nothing to do")
            logger.info("No action required, table already exists.")
            return True, "No action required, table already exists."

    @staticmethod
    def poll_master_table():
        """my doc is my string, verify me"""
        masterdblist = DatabaseSetup.write_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name='transactions'"
        )
        try:
            checktables = masterdblist.fetchone()
            logger.info(f"Master table checked and {checktables} table was found")
            return True, f"Master table checked and {checktables} table was found"
            # print("try")
        except IndexError:
            logger.warning("Index Error: Transaction table was not found.")
            return False, "Transaction table was not found."


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
        # and change nothing and save, it wont create duplicates but any unprotected fields: aka
        # post_date, tags, notes in the new conflicting data can overwrite/NULL the data
        # already in the DB.  I need better data integrity handling somehow
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


def load_db_to_dataframe(load_query: dict) -> pd.DataFrame:
    # THIS IS THE LIVE AND WORKING ONE
    """
    This should run a query using year and/or year and month against the expenses table and return
    the contents as a pandas dataframe.
    """
    dbconn = sqlite3.connect(default_database)
    if "All" in load_query["year"]:
        year_match = "-"
    else:
        year_match = load_query["year"]
    if "Whole" in load_query["month"]:
        # If whole year is selected then the query matches just the year in both cases
        month_match = year_match
    else:
        # else converts the month to the standard two digit month and the query uses both
        month_match = datetime.strptime(load_query["month"], "%b").strftime("%m")
        month_match = f"-{month_match}-"
    db_query = """
    SELECT *
    FROM transactions WHERE INSTR("Transaction Date", :year) > 0
    AND INSTR("Transaction Date", :month) > 0 ;
    """
    loaded_frame = pd.read_sql(
        db_query, dbconn, params={"year": year_match, "month": month_match}
    )
    # print(loaded_frame)
    return loaded_frame


def write_to_expenses(writedata="", live_expense_database=default_database):
    # I dont think this is currently used anymore
    """my doc is my string, verify me"""
    dbconn = sqlite3.connect(live_expense_database)
    writeCursor = dbconn.cursor()
    try:
        writeCursor.execute(writedata)
        dbconn.commit()
    except SyntaxError as e:
        print("Error executing query: ", e)
    writeCursor.close()


##### read-only database functions  ########


def query_by_month(
    month,
    live_expense_database=default_database,
    expenses_table=expenseTable,
):
    """my doc is my string, verify me"""
    dbconn = sqlite3.connect(live_expense_database)
    readCursor = dbconn.cursor()
    monthQuery = f"SELECT date, charge_name, amount, tag_id, notes FROM {expenses_table} WHERE\
        date LIKE '{month}%'"
    try:
        readCursor.execute(monthQuery)
        monthlyExpenses = readCursor.fetchall()
    except SyntaxError as e:
        print("Unable to execute for for reason: ", e)
        monthlyExpenses = e
    readCursor.close()
    return monthlyExpenses


def query_by_yearly_table(
    expenses_table=expenseTable, live_expense_database=default_database
):
    """my doc is my string, verify me"""
    dbconn = sqlite3.connect(live_expense_database)
    readCursor = dbconn.cursor()
    # Specify exact columns so you always know what you are getting back and dont get
    # 'too many values' errors
    recordquery = (
        f"SELECT date, charge_name, amount, tag_id, notes FROM {expenses_table}"
    )
    # print(recordquery)
    try:
        readCursor.execute(recordquery)
        fulltable = readCursor.fetchall()
    except SyntaxError as e:
        print("unable to execute query for reason: ", repr(e))
        fulltable = e
    readCursor.close()
    return fulltable


##### maintenance functions ######


def removeDuplicates(
    expenseDB=default_database,
    expenses_table=expenseTable,
):
    # Not currently used
    """my doc is my string, verify me"""
    dbconn = sqlite3.connect(expenseDB)
    writeCursor = dbconn.cursor()
    rowquery = f"SELECT MIN(rowid) FROM {expenses_table} group by charge_date, charge_name, amount"
    print(rowquery)
    deletedupes = f"DELETE FROM {expenses_table} WHERE rowid not in({rowquery})"
    print(deletedupes)
    removalResult = writeCursor.execute(deletedupes)
    print(removalResult)
    dbconn.commit()
    writeCursor.close()


if __name__ == "__main__":

    print(
        "I'm a library of database functions.  I dont think you meant to run this directly."
    )
