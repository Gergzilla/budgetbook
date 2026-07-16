#!/usr/bin/python
"""This module is classes and functions relating to managin the gui and it's unique elements.
Such as creating tabs and handling custom dialog boxes for various things"""

# I need to add I think a button making class that will
# create buttons at a fixed height and dynamic width of the text

from PyQt6.QtCore import Qt

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
from ..vars import settings

# specific year and month selectors for reports and summaries
year_selector = settings.year_list
year_selector.append("All")

month_selector = settings.month_dict
month_selector["Whole Year"] = "All"


class BudgetBookDialog(QDialog):
    """Base class for custom dialog boxes"""

    def __init__(self, mainwindow, modal=False):
        "initialize the dialog window, if modal is false base on the top level window"
        flag = Qt.WindowType.Dialog

        # if not modal:
        #     flag |= (
        #         Qt.WindowType.CustomizeWindowHint |
        #         Qt.WindowType.WindowMinimizeButtonHint |
        #         Qt.WindowType.WindowMaximizeButtonHint |
        #         Qt.WindowType.WindowCloseButtonHint |
        #         Qt.WindowType.WindowTitleHint |
        #         Qt.WindowType.WindowSystemMenuHint
        #     )

        QDialog.__init__(self, mainwindow, flag)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.mainwindow = mainwindow


class StandardDialogLayout(BudgetBookDialog):
    """Standard dialog layout with a menu bar, preview area, options entries, and confirmation buttons."""

    def __init__(self, parent, title="Standard Dialog", preview_text="Preview text goes here.", options=None):
        BudgetBookDialog.__init__(self, parent)
        self.setWindowTitle(str(title))

        self.menu_bar = QWidget()
        self.menu_bar.setObjectName("standardDialogMenuBar")
        menu_layout = QHBoxLayout()
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(4)
        self.menu_bar.setLayout(menu_layout)

        for menu_name in ("File", "Edit", "View"):
            menu_button = QPushButton(menu_name)
            menu_button.setFlat(True)
            menu_layout.addWidget(menu_button)

        menu_layout.addStretch()

        self.preview_label = QLabel(str(preview_text))
        self.preview_label.setWordWrap(True)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.preview_label.setMinimumHeight(120)

        self.options_layout = QVBoxLayout()
        self.option_entries = []

        if options is None:
            options = {
                "Option 1": ["Choice A", "Choice B", "Choice C"],
                "Option 2": ["First", "Second", "Third"],
            }

        for label_text, values in options.items():
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)
            row_widget.setLayout(row_layout)

            row_label = QLabel(label_text)
            row_combo = QComboBox()
            row_combo.addItems([str(value) for value in values])
            self.option_entries.append(row_combo)

            row_layout.addWidget(row_label)
            row_layout.addWidget(row_combo)
            self.options_layout.addWidget(row_widget)

        button_set = (
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box = QDialogButtonBox(button_set)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(self.menu_bar)
        dialog_layout.addWidget(self.preview_label)
        dialog_layout.addLayout(self.options_layout)
        dialog_layout.addWidget(self.button_box)
        self.setLayout(dialog_layout)


class FileImportDialog(BudgetBookDialog):
    import_folder = "."

    def __init__(self, parent, document):
        BudgetBookDialog.__init__(self, parent)
        self.document = document

        # whether import is ready to process

        self.previewisaccepted = False

        # Tab collection for import dialog
        self.tabs = {}


class CustomOkCancelDialog(QDialog):
    """my doc is my string, verify me"""

    def __init__(self, box_title: str, prompt_message: str):
        super().__init__()
        self.name = __name__
        self.box_title = str(box_title)
        self.prompt_message = str(prompt_message)
        self.setWindowTitle(str(self.box_title))

        qbutton_set = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box = QDialogButtonBox(qbutton_set)
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
    """This creates a custome input dialog to choose year or month
    and year for various date selections"""

    def __init__(self, dialog_type, parent=None):
        super().__init__(parent)
        self.name = __name__
        self.dialog_type = dialog_type
        self.setWindowTitle("Choose Data Range")
        # R0902: Too many instance attributes (9/7) (too-many-instance-attributes)
        # I should probably condense the dialog options into a dict or a dedicated function
        self.date_dialog_layout = QVBoxLayout()
        self.year_layout = QHBoxLayout()
        self.month_layout = QHBoxLayout()
        self.chosen_year = QComboBox()
        self.chosen_month = QComboBox()
        self.year = ""
        self.month = ""
        # print(f"chosen dialoge type is: {self.dialog_type}")

    def set_dialog_type(self, dialog_type: str = "year_only"):
        """Sets the type of custom dialog box to select year or month and year"""
        self.dialog_type = dialog_type
        if self.dialog_type == "year_only":
            # print(f"you chose {dialog_type}")
            self.year_layout.addWidget(QLabel("Select Year: "))
            self.chosen_year.addItems(year_selector)
            self.year_layout.addWidget(self.chosen_year)
            self.date_dialog_layout.addLayout(self.year_layout)

        elif self.dialog_type == "month_and_year":
            # print(f"you chose {dialog_type}")
            self.year_layout.addWidget(QLabel("Select Year: "))
            self.chosen_year.addItems(year_selector)
            self.year_layout.addWidget(self.chosen_year)
            self.month_layout.addWidget(QLabel("Select Year: "))
            self.chosen_month.addItems(month_selector)
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
        """hook for accept button to return selected values from the dialog"""
        if self.dialog_type == "year_only":
            self.year = self.chosen_year.itemText(self.chosen_year.currentIndex())
        elif self.dialog_type == "month_and_year":
            self.month = self.chosen_month.itemText(self.chosen_month.currentIndex())
            self.year = self.chosen_year.itemText(self.chosen_year.currentIndex())
        super().accept()

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
