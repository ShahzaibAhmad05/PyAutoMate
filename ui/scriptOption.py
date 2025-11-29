from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap
import logging
import os
import inspect
import pickle
from modules.sysUtils import sleep_for
from Assistant import GlobalTextBox
import threading
import json
import time
import sys
import shutil
import pyautogui
import keyboard
import mouse
from typing import Callable
import pyperclip
from io import BytesIO
import random
from PIL import Image
import webbrowser
import psutil
from pygetwindow import getActiveWindow, getWindowsWithTitle
from PyQt5.QtWidgets import (QPushButton,
                            QDialog, QMessageBox, QVBoxLayout,
                            QTextEdit, QFileDialog, QRadioButton,
                            QButtonGroup, QMenu, QInputDialog, QLineEdit,
                            QCheckBox, QSpinBox)
from PyQt5.QtCore import QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QTextCharFormat, QSyntaxHighlighter, QColor, QPainter, QCursor, QFont
from modules.styling import dialog_window_stylesheet
from modules.utils import enable_dragging
from ui.toggleSwitch import ToggleSwitch

class ScriptOption(QDialog):
    def __init__(self, parent, ok_button_name: str, functions: dict[str, Callable]=None, 
                 radios: list[str]=None, inputs: list[str]=None):
        super().__init__()

        self.parent = parent
        self.setWindowTitle('Select An Option')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setFixedWidth(self.parent.app_size * 7)
        title_bar_widget = dialog_window_stylesheet(self, parent)
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(self)
        main_widget.setLayout(main_layout)

        if radios:
            self.radio_group = QButtonGroup(self)
            self.radio_buttons_temp = []
            # setup the radio buttons
            for radio in radios:
                self.radio = QRadioButton(radio, self)
                self.radio_group.addButton(self.radio)
                main_layout.addWidget(self.radio)
                self.radio_buttons_temp.append(self.radio)
            self.radio.setStyleSheet("margin-bottom: 15px;")
            self.radio_buttons_temp[0].setChecked(True) # checks the first button of the group

        if functions:
            # setup the clickable buttons
            for key, value in functions.items():
                self.button = QPushButton(key, self)
                self.button.setObjectName("QPushButton")
                self.button.clicked.connect(value)
                main_layout.addWidget(self.button)

        if inputs:
            # values are taken by self.input_values.text()
            self.input_values = []
            for label in inputs:
                self.input_label = QLabel(label, self)
                main_layout.addWidget(self.input_label)
                self.line_edit = QLineEdit(self)
                self.input_values.append(self.line_edit)
                main_layout.addWidget(self.line_edit)
            self.input_values[0].setFocus()
        self.ok_button = QPushButton(ok_button_name, self)
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setObjectName("QPushButton")
        main_layout.addWidget(self.ok_button)
        overall_layout = QVBoxLayout(self)
        overall_layout.addWidget(title_bar_widget)
        overall_layout.addWidget(main_widget)
        self.setLayout(overall_layout)
        enable_dragging(self)

    def get_selected_option(self: QWidget) -> str:
        """ Returns the text of the selected radio button """
        selected_radio = self.radio_group.checkedButton()
        return selected_radio.text()
    
    def get_input_values(self: QWidget) -> list:
        """ returns a list of the references to the line edits """
        return self.input_values
    