#!/usr/bin/python

import pandas as pd
import os
import sys
import random
from dateutil.parser import parse as dateparse

from PyQt6.QtGui import QColor, QFont, QPen
from PyQt6.QtCharts import QChartView, QPieSeries, QChart, QPieSlice
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
    QInputDialog,
)

import utilities.handlers as handlers
import utilities.db_handlers as db_handlers
import utilities.gui_handlers as gui_handlers

# import utilities.importers.importers as importers

try:
    # Required as if -h is passed the program should exit cleanly
    from utilities.logger import LoggingHandler
except Exception:
    quit()

logger = LoggingHandler(str(os.path.basename(__file__))).log

# List of years to use for various prompts
year_list = ["2025", "2024", "2023", "2022", "2021", "2020"]
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
    "Whole Year": "All",
}
# specific year selector for reports and summaries
year_selector = year_list
year_selector.append("All")


def random_color_gen() -> str:
    R = random.randint(0, 255)
    G = random.randint(0, 255)
    B = random.randint(0, 255)
    color_string = f"#{R:02x}{G:02x}{B:02x}"
    return color_string


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = LoggingHandler(__class__).log
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
        self.report_tab_content_layout = QVBoxLayout()

        report_tab_year_label = QLabel("Select Year")
        self.report_tab_year_select = QComboBox()
        self.report_tab_year_select.addItems(year_selector)
        self.report_tab_year_select.setFixedSize(100, 30)
        report_tab_month_label = QLabel("Select Month")
        self.report_tab_month_select = QComboBox()
        self.report_tab_month_select.addItems(month_dict)
        self.report_tab_month_select.setFixedSize(100, 30)
        self.repor_tab_refresh_button = QPushButton("Refresh")
        self.repor_tab_refresh_button.setFixedSize(80, 30)

        self.report_tab_button_layout.addWidget(report_tab_year_label)
        self.report_tab_button_layout.addWidget(self.report_tab_year_select)
        self.report_tab_button_layout.addWidget(report_tab_month_label)
        self.report_tab_button_layout.addWidget(self.report_tab_month_select)
        self.report_tab_button_layout.addWidget(self.repor_tab_refresh_button)
        self.report_tab_button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.report_tab_pie_series = QPieSeries()
        self.report_tab_pie_series.setHoleSize(
            0.2
        )  # not required, left for visual testing

        report_slice1 = self.report_tab_pie_series.append("Mortage 30 pct", 30)
        report_slice2 = self.report_tab_pie_series.append("Utilies 5 pct", 5)
        report_slice3 = self.report_tab_pie_series.append("Grocery 20 pct", 20)
        report_slice4 = self.report_tab_pie_series.append("Restuarant 15 pct", 15)
        report_slice5 = self.report_tab_pie_series.append("Clothing 10 pct", 10)
        report_slice6 = self.report_tab_pie_series.append("Misc 20 pct", 20)

        # color tags use random color gen for simplicity.
        report_slice1.setBrush(QColor(random_color_gen()))
        report_slice2.setBrush(QColor(random_color_gen()))
        report_slice3.setBrush(QColor(random_color_gen()))
        report_slice4.setBrush(QColor(random_color_gen()))
        report_slice5.setBrush(QColor(random_color_gen()))
        report_slice6.setBrush(QColor(random_color_gen()))

        self.report_tab_pie_series.setLabelsVisible(True)
        pie_labels_font = QFont("Arial", 22)
        pie_labels_font.setBold(True)
        # need to find if its possible to set the slice font for all of them at once

        self.report_tab_chart = QChart()
        # self.report_tab_chart.setFont(pie_labels_font)
        self.report_tab_chart.addSeries(self.report_tab_pie_series)
        self.report_tab_chart.setTitle("Expense Report Demo Chart")
        self.report_tab_chart.setTitleFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.report_tab_chart.legend().setVisible(True)
        # self.report_tab_chart.legend().setFont(font object) this sets legend font
        self.report_tab_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        # Hide axes as they are not typically used for pie charts
        self.report_tab_chart.createDefaultAxes()  # Creates default axes first
        # these are wrong
        # self.report_tab_chart.axes(Qt.Orientation.Horizontal)[0].setVisible(False)
        # self.report_tab_chart.axes(Qt.Orientation.Vertical)[0].setVisible(False)

        self.report_tab_chart_view = QChartView(self.report_tab_chart)
        # left this off for now self.report_tab_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing) # For smoother rendering
        self.report_tab_content_layout.addWidget(self.report_tab_chart_view)

        self.report_tab_widget.tab_layout.addLayout(self.report_tab_button_layout)
        self.report_tab_widget.tab_layout.addLayout(self.report_tab_content_layout)
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
        self.data_table_model = handlers.PandasAbstractTable(blank_data)
        self.data_table_view = QTableView()
        self.data_table_view.setModel(self.data_table_model)

        # self.data_table_view.setEditTriggers(
        #     QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.AnyKeyPressed
        # )  # This doesnt currently work in my app but it did in testing.

        # Data Tab Buttons
        self.data_tab_button_layout = QHBoxLayout()
        self.import_data_button = QPushButton("Import File")
        self.import_data_button.clicked.connect(self.button_import_clicked)

        self.save_to_db_button = QPushButton("Save to Database")
        self.save_to_db_button.clicked.connect(self._save_to_database)  # NYI

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

    # Menu and button functions

    def _reset_table(self) -> None:
        blank_data = pd.DataFrame(
            [
                ["", "", "", "", ""],
            ],
            columns=["Charge Date", "Charge Name", "Charge Amount", "Tag", "Notes"],
            index=["0"],
        )
        self.data_table_model.update_table_from_dataframe(blank_data)

    def _save_to_database(self, current_table: pd.DataFrame):
        print("Saving table contents to database")
        db_handlers.save_dataframe_to_db(self.transaction_table)

    def button_quit_clicked(self) -> None:
        confirm_quit = gui_handlers.CustomOkCancelDialog(
            "Quit?", "Are you sure you want to quit?"
        )
        if confirm_quit.exec():
            sys.exit(0)
        else:
            pass

    def _choose_import_year(self) -> int:
        import_year, ok = QInputDialog.getItem(
            self, "What year is this data for?", "Select Year:", year_list, 0, False
        )
        if ok and import_year:
            # print(f"Year selected was {import_year}")
            return import_year

    def button_import_clicked(self) -> None:
        import_year = self._choose_import_year()
        print(f"Year returned was {import_year}")

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
                self.transaction_table = handlers.import_file_dialogue(
                    import_filename[0], import_year
                )
                # import works, there was an issue with the pdf parsing and column count in the pdf_importers module
                print("Data import complete")
                try:
                    self.data_table_model.update_table_from_dataframe(
                        self.transaction_table
                    )
                    self.data_table_view.resizeColumnsToContents()
                    self.data_table_view.setEditTriggers(
                        QTableView.EditTrigger.DoubleClicked
                        | QTableView.EditTrigger.AnyKeyPressed
                    )  # this works now, missed flag function in table class
                    # print(self.data_table_view.editTriggers())
                except Exception as e:
                    print(e)

        except:
            pass

    def _summary_query_by_year(self, year: int) -> pd.DataFrame:
        # pass through to call summary function against database
        try:
            return
            print(f"year chosen was {year}")
        except Exception as e:
            print(f"oops {e}")

    def _table_query_by_year(self, year: int) -> pd.DataFrame:
        try:
            return
            print(f"year chosen was {year}")
        except Exception as e:
            print(f"oops {e}")

    def deleteDupes(self):
        # left as a reminder, this function will be moved to the admin tab for obvious reasons.
        db_handlers.removeDuplicates()
        # delete_duplicates_button = QPushButton(text="delete duplicates", parent=self)
        # delete_duplicates_button.setFixedSize(200, 20)


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
