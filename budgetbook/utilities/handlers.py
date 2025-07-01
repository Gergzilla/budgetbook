#!/usr/bin/python
# This file is a copy of handlers.py but is being modified for django integration and testing
import os
import csv
import pandas as pd
import random
from dateutil.parser import parse as dateparse
from datetime import datetime

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtSql import QSqlQueryModel
from PyQt6.QtGui import QColor, QFont, QPen
from PyQt6.QtCharts import QChartView, QPieSeries, QChart, QPieSlice


from vars import settings
from utilities.logger import LoggingHandler
from utilities import db_handlers
from utilities import importers


# try:
#     import utilities.db_handlers as db_handlers
# except Exception:
#     import db_handlers as db_handlers

month_selector = settings.month_selector
logger = LoggingHandler(str(os.path.basename(__file__))).log


class PandasAbstractTable(QAbstractTableModel):
    # moved from handlers for testing
    # https://www.pythonguis.com/tutorials/pyqt6-qtableview-modelviews-numpy-pandas/
    def __init__(self, data: pd.DataFrame, parent=None):
        super().__init__(parent)
        # self.name = __name__
        self.logger = LoggingHandler(__class__).log
        self._data = data

    def flags(self, index) -> Qt.ItemFlag:
        """my doc is my string, verify me"""
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

    def rowCount(self, index, parent=QModelIndex()):
        """my doc is my string, verify me"""
        return self._data.shape[0]

    def columnCount(self, index, parent=QModelIndex()):
        """my doc is my string, verify me"""
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        """my doc is my string, verify me"""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """my doc is my string, verify me"""
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

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """my doc is my string, verify me"""
        if role == Qt.ItemDataRole.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            # Emit the dataChanged signal to notify the view

            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def update_table_from_dataframe(self, new_dataframe: pd.DataFrame) -> None:
        """my doc is my string, verify me"""
        # print(f"start reset function")
        # print(f"start reset function, dataframe contains:\n {new_dataframe}")
        self.beginResetModel()
        self._data = new_dataframe
        self.endResetModel()

        # print("Model reset completely. beginResetModel/endResetModel emitted.")


class QtPieChartSeries(QPieSeries):
    """my doc is my string, verify me"""

    # currently a placeholder while I figure out how I want to implement this
    def __init__(self, pie_dict: dict = {}, parent=None):
        super().__init__(parent)
        self.name = __name__
        self.logger = LoggingHandler(__class__).log
        self.pie_dict = pie_dict
        self.setHoleSize(0.2)  # arbitrary, may change later

        for category, value in self.pie_dict.items():
            self.value = value
            self.pie_label = str(category.split(" ")[0]) + " $" + str(self.value)
            self.slice = self.pie_label.split(" ")[0]
            self.slice = self.append(self.pie_label, self.value)
            self.slice.setBrush(QColor(random_color_gen()))

        self.setLabelsVisible(True)


####### Misc utilities  #######
def dateCheck(datestring, fuzzy=False):
    """my doc is my string, verify me"""
    try:
        dateparse(datestring, fuzzy=fuzzy)
        return True
    except Exception as e:
        # e isnt used but caught for proper handling, this just needs to
        # evaluate as false if it cant parse the date for any reason
        return False


def random_color_gen() -> str:
    """my doc is my string, verify me"""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    color_string = f"#{r:02x}{g:02x}{b:02x}"
    return color_string


####### File Handlers ########


def import_file_dialogue(import_file_name, import_year: int = 0):
    """my doc is my string, verify me"""
    try:
        print(f"import file is: {import_file_name}")
        # parse the file type of the import to try and select the right import method
        file_type = str(import_file_name).split(".")[1]
        # print(f"file_type is: {file_type}")
        if "csv" in file_type:
            # print("CSV file detected")
            transaction_data = importers.file_import_handlers.csvImporter(
                import_file_name, import_year
            )
        elif "pdf" in file_type:
            # print(" file detected")
            # hardcoded to capital one for now.  More advanced selection to be handled later
            transaction_data = importers.file_import_handlers.cap_one_import(
                import_file_name, import_year
            )
        return transaction_data
    except Exception as e:
        print(e)
        return


####### Parsers and Writers ########


# The expenseChunks and writeExpenseToDB are probably not needed anynmore.  I am converting all
# data data sources into pandas dataframes for better universal functionality and so there
# should not be a case where I need to parse massive lists to write to the db anymore.  will
# deprecate in later versions
def expense_chunks(expenseList, chunkSize):
    """my doc is my string, verify me"""
    print(
        f"Deprecation warning, the function {__name__} is being deprecated, if you got this message\
            Check what is using it as it should be migrated to db_handlers.save_dataframe_to_db()"
    )
    # this should take the list and return tuples of size chunkSize for all data sent to it
    for i in range(0, len(expenseList), chunkSize):
        yield expenseList[i : i + chunkSize]


def writeExpenseToDB(expenses) -> bool:
    """
    This should bring in all data provided to it in a list form, most likely from parsing the box
    contents and then prepare that data to be written to the sqlite database cleanly
    """
    print(
        f"Deprecation warning, the function {__name__} is being deprecated, if you got this message\
            check what is using it as it should be migrated to db_handlers.save_dataframe_to_db()"
    )
    for expense_batch in expense_chunks(expenses, 5):
        # print(expense_batch)
        result = db_handlers.saveExpensesToDB(expense_batch)
    if result:
        logger.error(result)
    else:
        print("messagebox.showinfo(message='All Entries saved to the Database')")
        # tkinter removed, confirmation should be changed to pyqt

        # db_handlers.addExpenses(expense_batch, "2024")


def monthlyQueryBuilder():  # rewriting for error handling on bad input
    """my doc is my string, verify me"""
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

if __name__ == "__main__":
    print(
        "I'm a collection of handler functions.  I dont think you meant to run this directly"
    )
