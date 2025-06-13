#!/usr/bin/python

import os
import sys


from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QTabWidget,
    QToolBar,
    QStatusBar,
    QDialog,
    QFileDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
)


class CustomOkCancelDialog(QDialog):
    def __init__(self, box_title: str, prompt_message: str):
        super().__init__()
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


class TabGenerator(QTabWidget):
    def __init__(self):
        super().__init__()
        self.__name__ = __name__
        self.tab_object = QWidget()
        self.tab_layout = QVBoxLayout()

    def setup_new_tab(self, label: str) -> QWidget:
        self.tab_label = QLabel(label)
        self.tab_layout.addWidget(self.tab_label)
        # self.tab_layout.addStretch()
        self.setLayout(self.tab_layout)
        return self.tab_object, self.tab_layout
