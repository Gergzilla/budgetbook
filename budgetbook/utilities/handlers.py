#!/usr/bin/python
# This file is a copy of handlers.py but is being modified for django integration and testing
import os
import csv
from PyQt6.QtWidgets import QLineEdit
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
import pandas as pd

# import itertools
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from dateutil.parser import parse as dateparse
from datetime import datetime
import vars.settings as settings
from utilities.logger import LoggingHandler
import utilities.db_handlers as db_handlers


# try:
#     import utilities.db_handlers as db_handlers
# except Exception:
#     import db_handlers as db_handlers

month_selector = settings.month_selector
logger = LoggingHandler(str(os.path.basename(__file__))).log

# the old TextBoxBuilder has been replaced with entry box handling because that is better.  The original POC is in its own file


class PandasTableDataDisplay(QtCore.QAbstractTableModel):
    # https://www.pythonguis.com/tutorials/pyqt6-qtableview-modelviews-numpy-pandas/
    def __init__(self, data):
        super().__init__()
        self.name = __name__
        self.logger = LoggingHandler(__class__).log
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

            # if isinstance(value, datetime):
            #     # Render time to YYY-MM-DD.
            #     return value.strftime("%Y-%m-%d")

            # if isinstance(value, float):
            #     # Render float to 2 dp
            #     return "%.2f" % value

            # if isinstance(value, str):
            #     # Render strings with quotes
            #     return '"%s"' % value

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])


class TableData(QtWidgets.QMainWindow):
    def __init__(self, dataframe):
        super().__init__()

        self.table = QtWidgets.QTableView()
        # print(f"self.data is: {self.data}")
        blank_data = pd.DataFrame(
            [
                ["", "", "", "", ""],
            ],
            columns=["Charge Date", "Charge Name", "Charge Amount", "Tag", "Notes"],
            index=["1"],
        )
        if dataframe == "":
            self.data = blank_data
        else:
            self.data = dataframe
        # self.model = PandasTableDataDisplay(self.data)
        self.model = PandasTableDataDisplay(self.data)
        self.table.setModel(self.model)

        self.setCentralWidget(self.table)


class EntryBoxBuilder:
    # original test moved to TextBoxBuilder_test.py

    def __init__(self, mainframe):
        self.name = __name__
        self.mainframe = mainframe
        self.logger = LoggingHandler(__class__).log
        # stringVar not currently used nor seems to be needed?
        self.dateBoxValue = StringVar()
        self.chargeBoxValue = StringVar()
        self.amountBoxValue = StringVar()
        self.tagBoxValue = StringVar()
        self.noteBoxValue = StringVar()

    def createEntryBoxRow(self, rowNumber):
        # print(f"createEntryBoxRow was called with expensedata: {expenses} \n And rowNumber of: {rowNumber}")
        BoxObjectList = []
        self.BoxObjectList = BoxObjectList
        dateBox = ttk.Entry(self.mainframe, width=12)
        chargeBox = ttk.Entry(self.mainframe, width=35)
        amountBox = ttk.Entry(self.mainframe, width=5)
        tagBox = ttk.Entry(self.mainframe, width=13)
        noteBox = ttk.Entry(self.mainframe, width=35)

        for r in range(rowNumber):
            rowSpacing = r + 1
            # print(f"row number: {r} and rowcount var {rowNumber}")
            dateBox.grid(column=1, row=rowSpacing, sticky=N, padx=1)
            chargeBox.grid(column=2, row=rowSpacing, sticky=N, padx=1)
            amountBox.grid(column=3, row=rowSpacing, sticky=N, padx=1)
            tagBox.grid(column=4, row=rowSpacing, sticky=N, padx=1)
            noteBox.grid(column=5, row=rowSpacing, sticky=N, padx=1)
        BoxObjectList.append(dateBox)
        BoxObjectList.append(chargeBox)
        BoxObjectList.append(amountBox)
        BoxObjectList.append(tagBox)
        BoxObjectList.append(noteBox)
        self.BoxObjectList = BoxObjectList

    def createEntryBoxes(self, rowcount):
        try:
            # this is the sidestep to using the input box for testing and isnt needed for now
            totalrows = int(rowcount.get())
        except Exception:
            totalrows = rowcount
        self.GlobalBoxList = []
        for row in range(totalrows):
            rowID = row + 1
            self.createEntryBoxRow(
                rowID
            )  # This works (forgot self.) and doesnt require input data
            for o in self.BoxObjectList:
                self.GlobalBoxList.append(o)
        # print(f"inside makeBoxes GlobalBoxList contains: {self.GlobalBoxList}")
        self.logger.debug(
            f"inside makeBoxes GlobalBoxList contains: {self.GlobalBoxList}"
        )
        # return self.BoxObjectList
        return self.GlobalBoxList

    def updateTextBox(self, expenses, rowcount):
        # Call createEntryBoxes which parses the imported file and creates enough rows for the data
        BoxObjects = self.createEntryBoxes(rowcount)
        # Call populateBoxes which populates each created box with the parsed data
        self.populateBoxes(expenses, BoxObjects)

    def populateBoxes(self, expenseList, boxList):
        i = 0
        while i < len(expenseList):
            boxList[i].insert(0, expenseList[i])
            i += 1

    def getBoxContents(self):
        self.GlobalExpenseData = []
        try:
            for contents in self.GlobalBoxList:
                self.GlobalExpenseData.append(contents.get())
                # print(contents.get())
            return self.GlobalExpenseData
        except AttributeError:
            messagebox.showwarning(message="Error: No data has been loaded yet")
            return


# End EntryBoxBiulder Class ================================================


####### Misc utilities  #######
def dateCheck(datestring, fuzzy=False):
    try:
        dateparse(datestring, fuzzy=fuzzy)
        return True
    except Exception as e:
        # e isnt used but its caught for proper coding, this merely needs to return false if it cant parse the date for any reason
        return False


####### File Handlers ########


def csvImporter(inputFileName, year="2025"):
    # Works perfectly!  results in a joined list of formatted data
    joinedCsv = []
    # For now we hardcode tab delim, need to do better handling later
    try:
        with open(inputFileName, newline="") as infile:
            infilereader = csv.reader(
                filter(lambda line: line.strip(), infile), delimiter=","
            )
            for row in infilereader:
                parsedRow, rowCount = parseCSV(row, year)
                for i in parsedRow:
                    joinedCsv.append(i)
        infile.close()
        return joinedCsv, rowCount
    except FileNotFoundError:
        logger.critical("No valid file was found to inport")


####### Parsers and Writers ########


def parseCSV(row, year):  # Works perfect!
    # New function to parse the csv one row at a time and reformat the data into a list of strings
    expenses = []
    i = 0
    date, charge_name, expense, tag, notes = "", "", "", "", ""
    while i < len(row):
        if row[i] != "":
            if dateCheck(row[i], fuzzy=False) is True:
                date = "'{}'".format(row[i])
                date = year + " " + str(date).strip("'")
                date = "{}".format(str(datetime.strptime(date, "%Y %b %d").date()))
                expenses.append(date)
            elif "$" in row[i]:
                expense = row[i].replace("$", "").strip("\n")
                expenses.append(expense)
                # adds empty list elements to the end as placeholders
                expenses.append(tag)
                expenses.append(notes)
            else:
                charge_name = "{}".format(row[i])
                # charge_name = "'{}'".format(row[i])
                expenses.append(charge_name)
            i += 1
        else:
            i += 1
    return expenses, i
    # print(f"Espenses prior to return: {expenses}")


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
        messagebox.showinfo(message="All Entries saved to the Database")
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
