#!/usr/bin/python
# This file is a copy of db_handlers.py but is being modified for django integration and testing
import sqlite3
import os
import pandas as pd
import vars.settings as settings

from utilities.logger import LoggingHandler

# try:
#     from utilities.logger import LoggingHandler
# except Exception:
#     from logger import LoggingHandler

#### Database Setup Functions #####
expenseDB = settings.expenseDB
expenseTable = settings.expenseTable
logger = LoggingHandler("db_handlers").log  # currenlty untested


class DatabaseSetup(object):
    def __init__(self):
        self.name = __name__
        self.logger = LoggingHandler(__class__).log
        pass

    def __str__(self):
        return self.name

    @staticmethod
    def createDB(expenseDB: str = expenseDB):
        # can prompt for db name in the future, for now its hard set
        if os.path.exists(expenseDB):
            # print("File exists, establishing connection to " + expenseDB)
            dbconnect = sqlite3.connect(expenseDB)
        else:
            print("Database File doesnt exist, creating file")
            logger.info("Database File doesnt exist, creating file")
            try:
                dbconnect = sqlite3.connect(expenseDB)
            except Exception:
                print("could not create file for some reason at " + expenseDB)
                logger.info("could not create file for some reason at " + expenseDB)
                dbconnect = ""
        return dbconnect

    @staticmethod
    def createBudgetTable(expenseDB: str = expenseDB) -> str:
        # create expenses table if it doesnt exist
        # this is disabled for now due to django integration
        dbconn = sqlite3.connect(expenseDB)
        writeCursor = dbconn.cursor()
        tableCheck = DatabaseSetup.pollMasterTable(writeCursor)
        print(tableCheck)
        if tableCheck == False:
            print("Table check is False, meaning table needs to be made")
            # print("do nothing")
            writeCursor.executescript(
                "CREATE TABLE transactions ('Transaction Date' TEXT, 'Post Date' TEXT, 'Charge Name' TEXT, 'Charge Amount' REAL, Tags TEXT, Notes TEXT, "
                "UNIQUE('Transaction Date','Charge Name','Charge Amount'))"
            )
            dbconn.commit()
            if DatabaseSetup.pollMasterTable:
                print("Table created")
            else:
                print("table still not found - something broke")
        else:
            print("Table check passed, nothing to do")
            return

    @staticmethod
    def pollMasterTable(cur):
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
    dbconn = sqlite3.connect(expenseDB)
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
        # this does create new entries without duplicates and allows for updates but if there are conflicts and data is empty it could overwrite
        # for example if you import the same file and chang enothing and save, it wont create duplicates but any unprotected fields:
        # aka post_date, tags, notes in the new conflicting data can overwrite/NULL the data already in the DB
        write_cursor.execute(
            "INSERT INTO transactions ('Transaction Date', 'Post Date', 'Charge Name', 'Charge Amount', Tags, Notes)"
            " VALUES (?,?,?,?,?,?) "
            'ON CONFLICT ("Transaction Date","Charge Name","Charge Amount") '
            "DO UPDATE SET 'Transaction Date' = excluded.'Transaction Date', 'Post Date' = excluded.'Post Date', 'Charge Name' = excluded.'Charge Name', "
            "'Charge Amount' = excluded.'Charge Amount', Tags = excluded.Tags, Notes = excluded.Notes",
            transaction_data,
        )

    dbconn.commit()
    # write_cursor.execute(
    #     "SELECT rowid, * FROM transactions WHERE charge_name IS NOT NULL"
    # )
    # rowlist = write_cursor.fetchall()
    # for row in rowlist:
    #     print(row)


def writeToExpenses(writedata="", expenseDB=expenseDB):
    dbconn = sqlite3.connect(expenseDB)
    writeCursor = dbconn.cursor()
    try:
        writeCursor.execute(writedata)
        dbconn.commit()
    except Exception as e:
        print("Error executing query: ", e)
    writeCursor.close()


# these last two functions need to be refactored because they are using the wrong SQL formatting AND need to update with hardcoded table name
def addExpenses(expensedata, year="2024", expenseTable="transactions"):
    # this is the proper format for insertion and works to auto increment ROWID
    # otherwise you can get a 'table has x columns but y supplied' unless you specificy the ROWID as well which isnt needed

    insertString = "INSERT INTO {0} (charge_date, charge_name, amount, tag_id, notes) VALUES ({1})".format(
        expenseTable, expensedata
    )  # bad form, but used to work. changing to placeholders
    print(insertString)
    writeToExpenses(insertString)


def addTag(expensdata, tag, year="2024", expenseTable="transactions"):
    # more learning, the for loop for a tuple doesnt work on a single item because there is nothing to iterate over
    # so here it is just a,b,c,y,z = tuple
    date, entity, charge, activetag, note = expensdata
    # activetag and note not needed here but allocated anyways to prevent ValueError
    tagUpdate = "UPDATE {0} SET tag='{1}' WHERE date='{2}' AND charge_name='{3}' AND amount={4}".format(
        expenseTable, tag, date, entity, charge
    )
    result = writeToExpenses(tagUpdate)
    return result


##### read-only database functions  ########


def queryByMonth(month, year="2024", expenseDB=expenseDB, expenseTable=expenseTable):
    dbconn = sqlite3.connect(expenseDB)
    readCursor = dbconn.cursor()
    monthQuery = "SELECT date, charge_name, amount, tag_id, notes FROM {0} WHERE date LIKE '{1}%'".format(
        expenseTable, month
    )
    try:
        readCursor.execute(monthQuery)
        monthlyExpenses = readCursor.fetchall()
    except Exception as e:
        print("Unable to execute for for reason: ", e)
        monthlyExpenses = e
    readCursor.close()
    return monthlyExpenses


def queryByYearlyTable(expenseTable=expenseTable, year="2024", expenseDB=expenseDB):
    dbconn = sqlite3.connect(expenseDB)
    readCursor = dbconn.cursor()
    # Specify exact columns so you always know what you are getting back and dont get 'too many values' errors
    recordquery = "SELECT date, charge_name, amount, tag_id, notes FROM {0}".format(
        expenseTable
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
    expenseDB=expenseDB, expenseTable=expenseTable, year="2024"
):  # Not currently used
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
        "I'm a library of database functions.  I dont think you meant to run this directly"
    )
