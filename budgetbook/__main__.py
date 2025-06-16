#!/usr/bin/python

import utilities.handlers as handlers
import utilities.db_handlers as db_handlers
import utilities.gui_handlers as gui_handlers
import utilities.importers.importers as importers
import pandas as pd
import os
import sys


from PyQt6.QtCore import QSize, Qt, QAbstractTableModel, QModelIndex, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QTabWidget,
    QToolBar,
    QStatusBar,
    QDialog,
    QFileDialog,
    QTableView,
    QDialogButtonBox,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QPushButton,
)
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from dateutil.parser import parse as dateparse

# from datetime import datetime

try:
    # Required as if -h is passed the program should exit cleanly
    from utilities.logger import LoggingHandler
except Exception:
    quit()

logger = LoggingHandler(str(os.path.basename(__file__))).log

year_selector = ["2025", "2024", "2023", "2022", "2021", "2020", "All"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Budget Book")
        self.setMinimumSize(QSize(1000, 800))

        # Setup Menu Menu Actions

        button_quit = QAction("&Quit", self)
        button_quit.setStatusTip("Exit Application")
        button_quit.triggered.connect(self.button_quit_clicked)

        button_import = QAction("&Import", self)
        button_import.setStatusTip("Import Expense File")
        button_import.triggered.connect(self.button_import_clicked)
        # file_menu.addAction(button_quit)

        # Setup Main Menu
        self.setStatusBar(QStatusBar(self))

        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_import)
        file_menu.addAction(button_quit)

        # Setup Tab Widget
        self.main_tabs = QTabWidget()
        self.setCentralWidget(self.main_tabs)
        self.main_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.main_tabs.setMovable(False)

        # Summary Tab
        self.summary_tab_widget = gui_handlers.TabGenerator()
        self.summary_tab_widget.setup_new_tab("Summary")

        self.summary_tab_button_layout = QHBoxLayout()
        self.summary_tab_button_layout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.summary_tab_display_layout = QVBoxLayout()

        self.summary_tab_main_label = QLabel("Main Label")
        self.summary_tab_secondary_label = QLabel("Secondary Label")
        self.summary_tab_year_select = QComboBox()
        # trigger change when selection changes
        self.summary_tab_year_select.currentTextChanged.connect(
            self._summary_query_by_year
        )
        self.summary_tab_year_select.addItems(year_selector)
        self.summary_tab_year_select.setFixedSize(100, 30)

        self.summary_tab_refresh = QPushButton("Refresh")
        self.summary_tab_refresh.setFixedSize(80, 30)

        # add buttons and labels to their layouts
        self.summary_tab_button_layout.addWidget(self.summary_tab_year_select)
        self.summary_tab_button_layout.addWidget(self.summary_tab_refresh)
        self.summary_tab_display_layout.addWidget(self.summary_tab_main_label)
        self.summary_tab_display_layout.addWidget(self.summary_tab_secondary_label)
        # add layouts to the tab
        self.summary_tab_widget.tab_layout.addLayout(self.summary_tab_button_layout)
        self.summary_tab_widget.tab_layout.addLayout(self.summary_tab_display_layout)
        self.summary_tab_widget.tab_layout.addStretch()

        # Report Tab
        self.report_tab_widget = gui_handlers.TabGenerator()
        self.report_tab_widget.setup_new_tab("Reports")
        self.report_tab_button_layout = QHBoxLayout()
        self.report_tab_year_select = QComboBox()
        self.report_tab_year_select.addItems(year_selector)

        self.report_tab_widget.tab_layout.addStretch()

        # Data Tab
        self.data_tab_widget = gui_handlers.TabGenerator()
        self.data_tab_widget.setup_new_tab("Data")

        # empty frame to just show standard columns for Data
        blank_data = pd.DataFrame(
            [
                ["", "", "", "", ""],
            ],
            columns=["Charge Date", "Charge Name", "Charge Amount", "Tag", "Notes"],
            index=["0"],
        )
        # Create pandas table object widget from handlers class
        self.data_table_model = handlers.PandasTableDataDisplay(blank_data)
        self.data_table_view = QTableView()
        self.data_table_view.setModel(self.data_table_model)

        self.data_table_view.setEditTriggers(
            QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.AnyKeyPressed
        )  # This doesnt currently work in my app but it did in testing.
        # self.data_table_view.resizeColumnsToContents() # this isnt needed here when there is no data for now

        # Data Tab Buttons
        self.data_tab_button_layout = QHBoxLayout()
        self.import_data_button = QPushButton("Import File")
        self.import_data_button.clicked.connect(self.button_import_clicked)

        self.save_to_db_button = QPushButton("Save to Database")
        # self.save_to_db_button.clicked.connect(self.write_to_db)  #NYI

        self.data_tab_reset_table_button = QPushButton("Reset Table Data")
        self.data_tab_reset_table_button.clicked.connect(self._reset_table)
        # add button widgets to the tabs layout
        self.data_tab_button_layout.addWidget(self.import_data_button)
        self.data_tab_button_layout.addWidget(self.save_to_db_button)
        self.data_tab_button_layout.addWidget(self.data_tab_reset_table_button)

        # add the data table widget and button layouts to the data tab
        self.data_tab_widget.tab_layout.addWidget(self.data_table_view)
        self.data_tab_widget.tab_layout.addLayout(self.data_tab_button_layout)

        # Admin Tab
        self.admin_tab = gui_handlers.TabGenerator()
        self.admin_tab.setup_new_tab("Admin")
        self.admin_tab.tab_layout.addStretch()

        # Add all tabs to the main tab widget
        self.main_tabs.addTab(self.summary_tab_widget, "Summary")
        self.main_tabs.addTab(self.report_tab_widget, "Reports")
        self.main_tabs.addTab(self.data_tab_widget, "Data")
        self.main_tabs.addTab(self.admin_tab, "Admin")

    def _reset_table(self):
        blank_data = pd.DataFrame(
            [
                ["", "", "", "", ""],
            ],
            columns=["Charge Date", "Charge Name", "Charge Amount", "Tag", "Notes"],
            index=["0"],
        )
        self.data_table_model.update_table_from_dataframe(blank_data)

        # Setup menu and button functions

    def button_quit_clicked(self):
        confirm_quit = gui_handlers.CustomOkCancelDialog(
            "Quit?", "Are you sure you want to quit?"
        )
        if confirm_quit.exec():
            sys.exit(0)
        else:
            pass

    def button_import_clicked(self):
        try:
            import_filename = QFileDialog.getOpenFileName(
                self,
                str("Open expense file"),
                "/scripts/pybudget/budgetbook/statements",
                str("Expense files (*.csv *.pdf *.xls *.xlsx)"),
            )
            # folder is hardcoded for now for dev convenience
            if import_filename[0] == "":
                return
            else:
                self.main_tabs.setCurrentWidget(self.data_tab_widget)
                # this dialogue should probably be its own window in order to validate the incoming data more easily
                # and then it can be saved to the database and then viewed and edited further in the main window.
                # we also need to add year selection combo box so the data is imported right.
                # I need to break out the actual import processing to the handlers module, this is too cluttered
                expenses = handlers.import_file_dialogue(import_filename[0])

                # expenses = pdf_importers.cap_one_import(import_filename[0])
                # import works, there was an issue with the pdf parsing and column count in the pdf_importers module
                print("Data import complete")
                try:
                    self.data_table_model.update_table_from_dataframe(expenses)
                    self.data_table_view.resizeColumnsToContents()
                    self.data_table_view.setEditTriggers(
                        QTableView.EditTrigger.DoubleClicked
                        | QTableView.EditTrigger.AnyKeyPressed
                    )  # this doesnt work here either
                except Exception as e:
                    print(e)
                # print("table view updated with import...maybe?")

        except:
            pass

    def _summary_query_by_year(self, year):
        # pass through to call summary function against database
        try:
            print(f"year chosen was {year}")
        except Exception as e:
            print(f"oops {e}")

    def _table_query_by_year(self, year):
        try:
            print(f"year chosen was {year}")
        except Exception as e:
            print(f"oops {e}")

        # buttons below were removed from main page for tab conversion, left to be used later as the functionality
        # is still needed in most cases and is a reference to the old UI layout but ported to PyQt6

        # view_expenses_button = QPushButton(text="View Expense Summar", parent=self)
        # view_expenses_button.setFixedSize(200, 20)
        # budget_report_button = QPushButton(text="View Budget Report", parent=self)
        # budget_report_button.setFixedSize(200, 20)
        # print_expenses_button = QPushButton(text="Print Expenses", parent=self)
        # print_expenses_button.setFixedSize(200, 20)
        # import_expenses_button = QPushButton(text="Import Expenses", parent=self)
        # import_expenses_button.setFixedSize(200, 20)
        # save_expenses_button = QPushButton(text="Save Expenses", parent=self)
        # save_expenses_button.setFixedSize(200, 20)
        # delete_duplicates_button = QPushButton(text="delete duplicates", parent=self)
        # delete_duplicates_button.setFixedSize(200, 20)
        # quit_button = QPushButton(text="Quit", parent=self)
        # quit_button.setFixedSize(200, 20)

        # main_window_layout = QVBoxLayout()

        # main_window_layout.addWidget(view_expenses_button)
        # main_window_layout.addWidget(budget_report_button)
        # main_window_layout.addWidget(print_expenses_button)
        # main_window_layout.addWidget(import_expenses_button)
        # main_window_layout.addWidget(save_expenses_button)
        # main_window_layout.addWidget(delete_duplicates_button)
        # main_window_layout.addWidget(quit_button)
        # main_window_layout.addWidget(main_tabs)
        # main_window_widget = QWidget()

        # main_window_widget.setLayout(main_window_layout)
        # self.setCentralWidget(main_window_widget)


# class removed for cleanup, methods left for conversion reference
#     def saveExpenses(self):
#         expenses = self.BoxMaking.getBoxContents()
#         handlers.writeExpenseToDB(expenses)

#     def printBoxContents(self):
#         try:
#             print(self.BoxMaking.getBoxContents())
#             # self.BoxMaking.print_box_data()
#         except AttributeError:
#             messagebox.showwarning(message="Error: No data has been loaded yet")
#             # print("Error: No data has been loaded yet")

#     def openFileImporter(self):

#         try:
#             expenses, rowcount = FileImportWindow(self)
#         except TypeError:
#             # If the import is cancelled or contains no data set empty values
#             expenses, rowcount = "", ""
#         if expenses or rowcount == "":
#             # If there is no data or if the user cancelled then do nothing
#             return
#         else:
#             # the returned information from the popup should give back these items
#             self.BoxMaking.updateTextBox(expenses, rowcount)

#     def deleteDupes(self):
#         db_handlers.removeDuplicates()

#     def leave(self):
#         try:
#             quit()
#         except Exception as e:
#             print(f"I have no idea how this failed but it was because of: {e}")


class FileImportWindow(Toplevel):
    # need to adapt this to PyQt6, currently tkinter method
    # 6-13-2025 file import dialogue has been ported but the extra input variables need to be added for data sanity
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Select budget file to import")
        self.geometry("400x400")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid(column=0, columnspan=3, row=0, rowspan=3, sticky=(N, W, E, S))
        self.yearChoice = ["2020", "2021", "2022", "2023", "2024", "2025"]
        self.fileType = ["CSV", "PDF"]
        self.importFilePrompt = StringVar()
        self.fileTypeSelection = StringVar()
        self.importYearSelection = StringVar()
        # Drop down lists and button to choose import file go here
        self.fileType = ttk.Combobox(
            self, textvariable=self.fileTypeSelection, values=self.fileType
        )
        self.fileType.grid(column=1, row=1, sticky=(N, W))
        self.importYear = ttk.Combobox(
            self, self.importYearSelection, values=self.yearChoice
        )
        self.importYear.grid(column=2, row=1, sticky=(N, W))

        # these are window controls to keep control to the popup dialogue window

        self.transient(master)  # open on top of main window
        self.grab_set()  # hijack all commands from master window
        master.wait_window(self)  # pause anything on main window until this closes

    def importFile(self):  # This works now, don't change it
        self.importFilePrompt.set(
            filedialog.askopenfilename(title="Select Expenses to Import")
        )
        importFile = self.importFilePrompt.get()
        if importFile == "":
            return
        else:
            expenses, rowcount = handlers.csvImporter(importFile)
            # Passes processed row count and expense list to update textboxes
            self.BoxMaking.updateTextBox(expenses, rowcount)


def main():
    try:
        with open("gui_style.css", "r") as f:
            stylesheet = f.read()
    except:
        stylesheet = ""

    main_app = QApplication(sys.argv)
    main_app.setStyleSheet(stylesheet)
    main_app.styleHints().setColorScheme(Qt.ColorScheme.Dark)
    main_window = MainWindow()
    main_window.show()
    sys.exit(main_app.exec())


if __name__ == "__main__":
    main()
