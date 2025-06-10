#!/usr/bin/python

import utilities.handlers as handlers
import utilities.db_handlers as db_handlers
import os
import sys


from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QDateEdit,
    QLabel,
    QPushButton,
    QLineEdit,
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


# converting tkinter window to class to handle multiple windows
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Budget Book")
        self.setMinimumSize(QSize(1000, 800))

        # Setup Tab Menus
        self.main_tabs = QTabWidget()
        self.main_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.main_tabs.setMovable(False)
        self.main_tabs.setStyleSheet(
            """
         QTabBar::tab {
             font-size: 12pt;
         }
     """
        )

        # Summary Tab
        summary_tab = QWidget()
        summary_layout = QVBoxLayout()
        summary_label = QLabel("Summary")
        summary_layout.addWidget(summary_label)
        summary_layout.addStretch()
        summary_tab.setLayout(summary_layout)
        self.main_tabs.addTab(summary_tab, "Summary")

        # Report Tab
        report_tab = QWidget()
        report_layout = QVBoxLayout()
        report_label = QLabel("Reports")
        report_layout.addWidget(report_label)
        report_layout.addStretch()
        report_tab.setLayout(report_layout)
        self.main_tabs.addTab(report_tab, "Reports")

        # Imports Tab
        imports_tab = QWidget()
        imports_layout = QVBoxLayout()
        imports_label = QLabel("Imports")
        imports_table = handlers.TableData()
        imports_layout.addWidget(imports_label)
        imports_layout.addWidget(imports_table)
        imports_layout.addStretch()
        imports_tab.setLayout(imports_layout)
        self.main_tabs.addTab(imports_tab, "Imports")

        # Report Tab
        updates_tab = QWidget()
        updates_layout = QVBoxLayout()
        updates_label = QLabel("Updates")
        updates_layout.addWidget(updates_label)
        updates_layout.addStretch()
        updates_tab.setLayout(updates_layout)
        self.main_tabs.addTab(updates_tab, "Updates")

        self.setCentralWidget(self.main_tabs)
        # Setup Main Buttons

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


# class MainWindow(ttk.Frame):
#     def __init__(self, master=None, **kwargs):
#         super().__init__(master, **kwargs)

#         ttk.Button(self, text="View Expense Summary", command="").grid(
#             column=8, row=2, sticky=(E, S)
#         )
#         ttk.Button(self, text="View Budget Report", command="").grid(
#             column=8, row=3, sticky=(E, S)
#         )
#         ttk.Button(self, text="Print Expenses", command=self.printBoxContents).grid(
#             column=8, row=4, sticky=(E, S)
#         )
#         ttk.Button(self, text="Import Expenses", command=self.openFileImporter).grid(
#             column=7, row=5, sticky=(E, S)
#         )
#         ttk.Button(self, text="Save Expenses", command=self.saveExpenses).grid(
#             column=8, row=5, sticky=(E, S)
#         )
#         ttk.Button(self, text="Quit", command=self.leave).grid(
#             column=8, row=6, sticky=(E, S)
#         )
#         ttk.Button(self, text="delete duplicates", command=self.deleteDupes).grid(
#             column=7, row=7, sticky=(E, S), padx=5, pady=10
#         )
#         # ttk.Button(mainframe, text="Print Box content", command=lambda: self.BoxMaking.print_box_data()).grid(column=8, row=8, padx=5, pady=5)
#         self.BoxMaking = handlers.EntryBoxBuilder(self)
#         self.importFilePrompt = StringVar()

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
    # root = Tk()
    # root.title("Welcome to MyPyBudget")
    # root.geometry("1024x800")
    # root.columnconfigure(0, weight=1)
    # root.rowconfigure(0, weight=1)

    # root.configure(background="DarkGray")
    # style = ttk.Style(root)
    # style.configure("TNotebook.Tab", width=root.winfo_screenwidth())

    # nb = ttk.Notebook(
    #     root,
    #     padding="8 8 12 12",
    #     width=root.winfo_screenmmwidth(),
    #     height=root.winfo_screenmmheight(),
    # )

    # # I need to check the formatting and layout, its broken now with the class
    # mainframe = MainWindow(nb)
    # mainframe.grid(column=0, columnspan=9, row=0, rowspan=9, sticky=(N, W, E, S))

    # nb.add(mainframe, text="Main")
    # nb.pack()
    # root.mainloop()

    main_app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(main_app.exec())


if __name__ == "__main__":
    main()
