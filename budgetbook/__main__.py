#!/usr/bin/python
"""my doc is my string, verify me"""
import os
import sys
import random

# from dateutil.parser import parse as dateparse
import pandas as pd

from PyQt6.QtCharts import QChartView, QChart
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QFont, QFontMetrics, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QStatusBar,
    QFileDialog,
    QTableView,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QPushButton,
    QInputDialog,
    QDialog,
)

from utilities import handlers
from utilities import db_handlers
from utilities import gui_handlers

# import utilities.importers.importers as importers

try:
    # Required as if -h is passed the program should exit cleanly
    from utilities.logger import LoggingHandler
except ImportError:
    sys.exit(0)

logger = LoggingHandler(str(os.path.basename(__file__))).log

# List of years to use for various prompts
# further note, these should be unified somewhere in vars file later
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

# Dictionary to convert database columns to user readable strings for displaying expenses
readable_columns = {
    "transaction_date": "Charge Date",
    "post_date": "Post Date",
    "transaction_name": "Charge Name",
    "transaction_amount": "Charge Amount",
    "tags": "Tags",
    "notes": "Notes",
}


def random_color_gen() -> str:
    """my doc is my string, verify me"""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    color_string = f"#{r:02x}{g:02x}{b:02x}"
    return color_string


class MainWindow(QMainWindow):
    """my doc is my string, verify me"""

    def __init__(self):
        super().__init__()
        self.logger = LoggingHandler(__class__).log
        self.setWindowTitle("Budget Book")
        self.setMinimumSize(QSize(1000, 800))
        current_font = self.font()
        self.font_metrics = QFontMetrics(current_font)
        # Setup Menu Menu Actions

        button_quit = QAction("&Quit", self)
        button_quit.setStatusTip("Exit Application")
        button_quit.triggered.connect(self._button_quit_clicked)

        button_import = QAction("&Import", self)
        button_import.setStatusTip("Import Expense File")
        button_import.triggered.connect(self.button_import_clicked)
        # file_menu.addAction(button_quit)
        # empty frame to just show standard columns for Data

        self.blank_table = pd.DataFrame(
            [
                ["", "", "", "", "", ""],
            ],
            columns=[
                "Transaction Date",
                "Post Date",
                "Charge Name",
                "Charge Amount",
                "Tags",
                "Notes",
            ],
            index=["0"],
        )
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
        self.summary_tab_widget.setup_new_tab()

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
        self.report_tab_widget.setup_new_tab()
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
        # self.report_tab_refresh_button = gui_handlers.PushButtonGenerator(
        #     ["Refresh", self.font_metrics.width("Refresh")]
        # )
        self.report_tab_run_report_button = QPushButton("Run Report")
        self.report_tab_run_report_button.setFixedSize(80, 30)
        self.report_tab_run_report_button.clicked.connect(self._generate_report_chart)

        self.report_tab_button_layout.addWidget(report_tab_year_label)
        self.report_tab_button_layout.addWidget(self.report_tab_year_select)
        self.report_tab_button_layout.addWidget(report_tab_month_label)
        self.report_tab_button_layout.addWidget(self.report_tab_month_select)
        self.report_tab_button_layout.addWidget(self.report_tab_run_report_button)
        self.report_tab_button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.pie_dict = {  # temp static data for chart generation
            "Mortage 30 pct": 180,
            "Utilies 5 pct": 5,
            "Grocery 20 pct": 20,
            "Restuarant 15 pct": 15,
            "Clothing 10 pct": 10,
            "Misc 20 pct": 20,
        }
        self.report_tab_pie_series = handlers.QtPieChartSeries(self.pie_dict)

        # self.report_tab_pie_series.setLabelsVisible(True)
        pie_labels_font = QFont("Arial", 22)
        pie_labels_font.setBold(True)
        # need to find if its possible to set the slice font for all of them at once

        self.report_tab_chart = QChart()
        # self.report_tab_chart.setFont(pie_labels_font)
        # the addSeries is the component we will modify with the generate report button
        # self.report_tab_chart.addSeries(self.report_tab_pie_series)
        self.report_tab_chart.setTitle("Expense Report Demo Chart")
        self.report_tab_chart.setTitleFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.report_tab_chart.legend().setVisible(True)
        # self.report_tab_chart.legend().setFont(font object) this sets legend font
        self.report_tab_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.report_tab_chart.createDefaultAxes()  # Creates default axes first

        self.report_tab_chart_view = QChartView(self.report_tab_chart)
        # left this off for now
        self.report_tab_chart_view.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )  # For smoother rendering
        self.report_tab_content_layout.addWidget(self.report_tab_chart_view)
        # I will be adding a small table display to view the data the pie chart uses for reference
        # later.

        self.report_tab_widget.tab_layout.addLayout(self.report_tab_button_layout)
        self.report_tab_widget.tab_layout.addLayout(self.report_tab_content_layout)
        self.report_tab_widget.tab_layout.addStretch()

        # Data Tab
        self.data_tab_widget = gui_handlers.TabGenerator()
        self.data_tab_widget.setup_new_tab()

        self.transaction_table = self.blank_table
        # Create pandas table object widget from handlers class
        self.data_table_model = handlers.PandasAbstractTable(self.transaction_table)
        self.data_table_view = QTableView()
        self.data_table_view.setModel(self.data_table_model)

        # Data Tab Buttons
        self.data_tab_button_layout = QHBoxLayout()

        self.import_data_button = QPushButton("Import File")
        self.import_data_button.clicked.connect(self.button_import_clicked)
        self.load_data_button = QPushButton("Load Month from Database")
        self.load_data_button.clicked.connect(self.button_load_from_db_clicked)
        self.save_to_db_button = QPushButton("Save to Database")
        self.save_to_db_button.clicked.connect(self._save_to_database)
        self.data_tab_reset_table_button = QPushButton("Reset Table Data")
        self.data_tab_reset_table_button.clicked.connect(self._reset_table)

        # add button widgets to the tabs layout
        self.data_tab_button_layout.addWidget(self.import_data_button)
        self.data_tab_button_layout.addWidget(self.load_data_button)
        self.data_tab_button_layout.addWidget(self.save_to_db_button)
        self.data_tab_button_layout.addWidget(self.data_tab_reset_table_button)

        # add the data table widget and button layouts to the data tab
        self.data_tab_widget.tab_layout.addWidget(self.data_table_view)
        self.data_tab_widget.tab_layout.addLayout(self.data_tab_button_layout)

        # Admin Tab
        self.admin_tab = gui_handlers.TabGenerator()
        self.admin_tab.setup_new_tab()
        self.admin_tab.tab_layout.addStretch()

        # Add all tabs to the main tab widget
        self.main_tabs.addTab(self.summary_tab_widget, "Summary")
        self.main_tabs.addTab(self.report_tab_widget, "Reports")
        self.main_tabs.addTab(self.data_tab_widget, "Data")
        self.main_tabs.addTab(self.admin_tab, "Admin")

    # Menu and button functions

    def _reset_table(self) -> None:
        """my doc is my string, verify me"""
        # Set the table to the empty dataframe and reset the view
        self.transaction_table = self.blank_table
        self.data_table_model.update_table_from_dataframe(self.transaction_table)

    def _save_to_database(self, current_table: pd.DataFrame):
        """my doc is my string, verify me"""
        # I need to rework the default view because if you attempt manual
        # entry without import it fails.
        print("Saving table contents to database")
        db_handlers.save_dataframe_to_db(self.transaction_table)

    def _generate_report_chart(self):
        """my doc is my string, verify me"""
        print("Generating report from _year_ and _month_")
        # so we need to call the report handler we will create in db_hanglers, and get the value of
        # the month and year selector and pass those to the function
        chosen_year = self.report_tab_year_select.itemText(
            self.report_tab_year_select.currentIndex()
        )
        chosen_month = self.report_tab_month_select.itemText(
            self.report_tab_month_select.currentIndex()
        )
        # current selection is finished, future change is dynamic update chart when selection changes
        print(f"chosen year is: {chosen_year} and chosen month is  {chosen_month}")
        # need to insert DB call to update the chart with.
        self.report_tab_pie_series = handlers.QtPieChartSeries(self.pie_dict)
        self.report_tab_chart.removeAllSeries()  # overwrites the one currently there
        self.report_tab_chart.addSeries(self.report_tab_pie_series)

    def _choose_date_range(self, type) -> int:
        # currently deprecated
        # This was moved to a custom dialog class to handle both month and year as needed
        """my doc is my string, verify me"""
        import_year, ok = QInputDialog.getItem(
            self, "What year is this data for?", "Select Year:", year_list, 0, False
        )
        if ok and import_year:
            # print(f"Year selected was {import_year}")
            return import_year
        return None

    def button_import_clicked(self) -> None:
        """my doc is my string, verify me"""
        import_year_dialog = gui_handlers.CustomDateRangeDialogue(self)
        import_year_dialog.set_dialog_type("year_only")
        import_year_range = import_year_dialog.exec()
        if import_year_range == QDialog.DialogCode.Accepted:
            import_year = import_year_dialog.year
            print(f"chosen year is: {import_year}")

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
            self.main_tabs.setCurrentWidget(self.data_tab_widget)
            # this dialogue should probably be its own window in order to validate the incoming
            # data more easily and then it can be saved to the database and then viewed and
            # edited further in the main window.
            self.transaction_table = handlers.import_file_dialogue(
                import_filename[0], import_year
            )
            # import works, there was an issue with the pdf parsing and column count in the
            # pdf_importers module
            print("Data import complete")
            try:
                # I need to add a formatter to make the column names look nice and pretty
                # without impacting the DB
                self.data_table_model.update_table_from_dataframe(
                    self.transaction_table
                )
                self.data_table_view.resizeColumnsToContents()
                self.data_table_view.setEditTriggers(
                    QTableView.EditTrigger.DoubleClicked
                    | QTableView.EditTrigger.AnyKeyPressed
                )  # this works now, missed flag function in table class
                # print(self.data_table_view.editTriggers())
            except ValueError as e:
                print(e)

        except ValueError as e:
            print(e)

    def button_load_from_db_clicked(self) -> None:
        print("did you click load data?")
        load_date_dialog = gui_handlers.CustomDateRangeDialogue(self)
        load_date_dialog.set_dialog_type("month_and_year")
        load_date_range = load_date_dialog.exec()
        if load_date_range == QDialog.DialogCode.Accepted:
            load_year = load_date_dialog.year
            load_month = load_date_dialog.month
            print(f"chosen year is: {load_year} and chosen month is  {load_month}")

    def _summary_query_by_year(self, year: int) -> pd.DataFrame:
        """my doc is my string, verify me"""
        # pass through to call summary function against database
        try:
            return
            # print(f"year chosen was {year}")
        except ValueError as e:
            print(f"oops {e}")

    def _button_quit_clicked(self) -> None:
        """my doc is my string, verify me"""
        confirm_quit = gui_handlers.CustomOkCancelDialog(
            "Quit?", "Are you sure you want to quit?"
        )
        if confirm_quit.exec():
            sys.exit(0)
        else:
            pass

    def delete_duplicates(self):
        """my doc is my string, verify me"""
        # left as a reminder, this function will be moved to the admin tab for obvious reasons.
        db_handlers.removeDuplicates()
        # delete_duplicates_button = QPushButton(text="delete duplicates", parent=self)
        # delete_duplicates_button.setFixedSize(200, 20)


def main():
    """my doc is my string, verify me"""
    try:
        with open("gui_style.css", "r", encoding="utf-8") as f:
            stylesheet = f.read()
    except FileNotFoundError:
        stylesheet = ""

    main_app = QApplication(sys.argv)
    main_app.setStyleSheet(stylesheet)
    main_app.styleHints().setColorScheme(Qt.ColorScheme.Dark)
    main_window = MainWindow()
    main_window.show()
    sys.exit(main_app.exec())


if __name__ == "__main__":
    main()
