#!/usr/bin/python
"""my doc is my string, verify me"""
# TODO I need to add I think a button making class that will
# create buttons at a fixed height and dynamic width of the text

# from PyQt6.QtCore import QSize, Qt
# from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QWidget,
    QTabWidget,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)

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


class CustomOkCancelDialog(QDialog):
    """my doc is my string, verify me"""

    def __init__(self, box_title: str, prompt_message: str):
        super().__init__()
        self.name = __name__
        self.box_title = str(box_title)
        self.prompt_message = str(prompt_message)
        self.setWindowTitle(str(self.box_title))

        Qbutton_set = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box = QDialogButtonBox(Qbutton_set)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        dialog_layout = QVBoxLayout()
        dialog_message = QLabel(self.prompt_message)
        dialog_layout.addWidget(dialog_message)
        dialog_layout.addWidget(self.button_box)
        self.setLayout(dialog_layout)

    def __str__(self):
        return self.name


class CustomDateRangeDialogue(QDialog):
    """This creates a customer input dialog to choose year or month and year for various date selections"""

    # this doesnt actually open a window for some reason
    def __init__(self, dialog_type, parent=None):
        super().__init__(parent)
        self.name = __name__
        self.dialog_type = dialog_type
        self.setWindowTitle("Choose Data Range")

        self.date_dialog_layout = QVBoxLayout()
        # print(f"chosen dialoge type is: {self.dialog_type}")

    def set_dialog_type(self, dialog_type):
        self.dialog_type = dialog_type
        if self.dialog_type == "year_only":
            print(f"you chose {dialog_type}")
            self.year_layout = QHBoxLayout()
            self.year_layout.addWidget(QLabel("Select Year: "))
            self.chosen_year = QComboBox()
            self.chosen_year.addItems(year_selector)
            self.year_layout.addWidget(self.chosen_year)

            self.date_dialog_layout.addLayout(self.year_layout)

        elif self.dialog_type == "month_and_year":
            print(f"you chose {dialog_type}")
            self.year_layout = QHBoxLayout()
            self.year_layout.addWidget(QLabel("Select Year: "))
            self.chosen_year = QComboBox()
            self.chosen_year.addItems(year_selector)
            self.year_layout.addWidget(self.chosen_year)

            self.month_layout = QHBoxLayout()
            self.month_layout.addWidget(QLabel("Select Year: "))
            self.chosen_month = QComboBox()
            self.chosen_month.addItems(month_dict)
            self.month_layout.addWidget(self.chosen_month)

            self.date_dialog_layout.addLayout(self.year_layout)
            self.date_dialog_layout.addLayout(self.month_layout)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        self.date_dialog_layout.addLayout(button_layout)

        self.setLayout(self.date_dialog_layout)

    def accept(self):
        if self.dialog_type == "year_only":
            self.year = self.chosen_year.itemText(self.chosen_year.currentIndex())
        elif self.dialog_type == "month_and_year":
            self.month = self.chosen_month.itemText(self.chosen_month.currentIndex())
            self.year = self.chosen_year.itemText(self.chosen_year.currentIndex())
        super().accept()

    def __str__(self):
        return self.name


class YearSelectDialogue(QDialog):  # not using yet, maybe never
    """my doc is my string, verify me"""

    def __init__(self, box_title: str, prompt_message: str):
        super().__init__()
        self.name = __name__
        self.box_title = str(box_title)
        self.prompt_message = str(prompt_message)
        self.setWindowTitle(str(self.box_title))

    def __str__(self):
        return self.name


class TabGenerator(QTabWidget):
    """my doc is my string, verify me"""

    def __init__(self):
        super().__init__()
        self.name = __name__
        self.tab_object = QWidget()
        self.tab_layout = QVBoxLayout()

    def setup_new_tab(self) -> QWidget:
        """my doc is my string, verify me"""
        # self.tab_label = QLabel(label) placeholed not needed now
        # self.tab_layout.addWidget(self.tab_label)
        self.setLayout(self.tab_layout)
        return self.tab_object, self.tab_layout

    def __str__(self):
        return self.name
