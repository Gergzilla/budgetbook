#!/usr/bin/python
# This file is a copy of handlers.py but is being modified for django integration and testing
import os
import csv
import pandas as pd
from dateutil.parser import parse as dateparse
from datetime import datetime

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtSql import QSqlQueryModel

import vars.settings as settings
from utilities.logger import LoggingHandler
import utilities.db_handlers as db_handlers
import utilities.importers.importers as importers


# try:
#     import utilities.db_handlers as db_handlers
# except Exception:
#     import db_handlers as db_handlers

month_selector = settings.month_selector
logger = LoggingHandler(str(os.path.basename(__file__))).log


class PandasTableDataDisplay(QAbstractTableModel):
    # moved from handlers for testing
    # https://www.pythonguis.com/tutorials/pyqt6-qtableview-modelviews-numpy-pandas/
    def __init__(self, data: pd.DataFrame, parent=None):
        super().__init__(parent)
        # self.name = __name__
        self.logger = LoggingHandler(__class__).log
        self._data = data

    def rowCount(self, index, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, index, parent=QModelIndex()):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            print("bad index")
            return None
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            try:
                value = self._data.iloc[index.row(), index.column()]
                # print(f"data function got value: \n {value}")
            except Exception as e:
                print(e)
            # print(f"The data function got the value:\n {value}")

            return str(value)
        return None

    def update_table_from_dataframe(self, new_dataframe: pd.DataFrame):
        # print(f"start reset function")
        # print(f"start reset function, dataframe contains:\n {new_dataframe}")
        self.beginResetModel()
        self._data = new_dataframe
        self.endResetModel()
        print("Model reset completely. beginResetModel/endResetModel emitted.")


####### Misc utilities  #######
def dateCheck(datestring, fuzzy=False):
    try:
        dateparse(datestring, fuzzy=fuzzy)
        return True
    except Exception as e:
        # e isnt used but caught for proper handling, this just needs to evaluate as false if it cant parse the date for any reason
        return False


####### File Handlers ########


def import_file_dialogue(import_file_name):

    try:
        print(f"import file is: {import_file_name}")
        # parse the file type of the import to try and select the right import method
        file_type = str(import_file_name).split(".")[1]
        # print(f"file_type is: {file_type}")
        if "csv" in file_type:
            # print("CSV file detected")
            transaction_data = importers.file_import_handlers.csvImporter(
                import_file_name
            )
        elif "pdf" in file_type:
            # print(" file detected")
            transaction_data = importers.file_import_handlers.cap_one_import(
                import_file_name
            )
        return transaction_data
    except Exception as e:
        print(e)
        return


####### Parsers and Writers ########


def expenseChunks(expenseList, chunkSize):
    # this should take the list and return tuples of size chunkSize for all data sent to it
    for i in range(0, len(expenseList), chunkSize):
        yield expenseList[i : i + chunkSize]


def writeExpenseToDB(expenses):
    """
    This should bring in all data provided to it in a list form, most likely from parsing the box contents
    and then prepare that data to be written to the sqlite database cleanly
    """
    for expense_batch in expenseChunks(expenses, 5):
        # print(expense_batch)
        result = db_handlers.saveExpensesToDB(expense_batch)
    if result:
        logger.error(result)
    else:
        print("messagebox.showinfo(message='All Entries saved to the Database')")
        # tkinter removed, confirmation should be changed to pyqt

        # db_handlers.addExpenses(expense_batch, "2024")


def parseToSQL(rawimport, year="2025"):
    # this was replaced by parseCSV, we need to create a new generic SQL prep function to write data to the DB
    # parse input data to sql data and call writeToDB
    i = 0
    date, charge_name, expense = "", "", ""
    csvline = rawimport.split("  ")
    while i < len(csvline):
        if csvline[i] != "":
            if dateCheck(csvline[i], fuzzy=False) is True:
                date = "'{}'".format(csvline[i])
                date = year + " " + str(date).strip("'")
                # Convert date to standard format for DB usage
                date = "'{}'".format(str(datetime.strptime(date, "%Y %b %d").date()))
                # print(date)
            elif "$" in csvline[i]:
                expense = csvline[i].replace("$", "")
            else:
                charge_name = "'{}'".format(csvline[i])
            i = i + 1
        else:
            i = i + 1
    # print(date + charge_name + expense)
    writeExpenseToDB(date, charge_name, expense)


def monthlyQueryBuilder():  # rewriting for error handling on bad input
    # not currently used in the UI
    month = ""
    month = input("Enter the name of the Month to modify: ").capitalize()
    while month not in month_selector:
        month = input(
            "That was not a valid choice.  Month must be a name or abbrev, e.g. Mar or March: "
        ).capitalize()
        month = "" + month[0:3]
        # print(month)
    else:
        print("looks fine, calling query")
        listByMonth = db_handlers.queryByMonth(month)
    return listByMonth


# def monthlyQueryBuilder(): original, works ok
#     month = input("Enter the name of the Month to modify: ").capitalize()
#     month = "" + month[0:3]
#     if month not in month_selector:
#         print("Month must be a name or abbrev, e.g. Mar or March")
#     else:
#         print("looks fine, calling query")
#         listByMonth = db_handlers.queryByMonth(month)
#     return listByMonth


def chooseExpenseToTag():
    print("nothing here yet")


def displayPrettyExpenses(queryresult):
    os.system("cls" if os.name == "nt" else "clear")
    i = 1
    for date, entity, expense, tag, notes in queryresult:
        print(i, date, entity, expense, tag, notes)
        i = i + 1


# def writeExpenseToDB(date, charge_name, expense, tag="' '", notes="' '"):
#     expensedata = date + "," + charge_name + "," + expense + "," + tag + "," + notes
#     print(expensedata)
#     db_handlers.addExpenses(expensedata, "2024")

if __name__ == "__main__":
    print("I'm a collection of functions.  I dont think you meant to run this directly")
