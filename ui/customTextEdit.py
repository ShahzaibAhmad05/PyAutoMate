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
from modules.styling import dialog_window_stylesheet, context_menu_stylesheet
from modules.utils import enable_dragging, add_spaces_for_context_menu
from ui.toggleSwitch import ToggleSwitch

# start of CustomTextEdit class
class CustomTextEdit(QTextEdit):
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        self.highlighter = KeywordHighlighter(self.document())
        self.setFixedHeight(self.parent.app_size * 7)

    def export_script(self):
        file_path, _ = QFileDialog.getSaveFileName(parent=self, caption='Export Script',
                                                    directory='code.txt', filter="Text Files (*.txt)")
        with open(file_path, 'w') as file:
            file.write(self.toPlainText())
        self.setFocus()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        text_to_add = add_spaces_for_context_menu('Copy All', 'Ctrl + L')
        action1 = menu.addAction(text_to_add)
        text_to_add = add_spaces_for_context_menu('Paste', 'Ctrl + V')
        action2 = menu.addAction(text_to_add)
        action4 = menu.addAction('Clear')
        menu.addSeparator()
        action6 = menu.addAction('Import Script')
        text_to_add = add_spaces_for_context_menu('Export Script', 'Ctrl + E')
        action5 = menu.addAction(text_to_add)
        action3 = menu.addAction("Help")
        menu.addSeparator()
        actione = menu.addAction("Back")
        context_menu_stylesheet(menu, self.parent)

        action = menu.exec_(event.globalPos())
        if action is None: return
        elif action == action2:
            self.insertPlainText(pyperclip.paste())
        elif action == action1:
            pyperclip.copy(self.toPlainText())
        elif action == action4:
            if (self.toPlainText().strip() and QMessageBox.warning(self, "PyAutoMate", 
                "The entire script will be cleared. Continue?", QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No)) == QMessageBox.Yes:
                self.clear()
            self.setFocus()
        elif action == action5 and self.toPlainText().strip():
            self.export_script()
        elif action == action6:
            file_path, _ = QFileDialog.getOpenFileName(parent=self, caption='Select Code File', filter="Text Files (*.txt)")
            with open(file_path, 'r') as file:
                content = file.read()
                self.insertPlainText(content)
            self.setFocus()
        elif action == actione:
            if (self.toPlainText().strip() and QMessageBox.warning(self, "PyAutoMate", 
                "The script will be discarded. Continue?", QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No)) == QMessageBox.Yes or not self.toPlainText().strip():
                self.reject()
            else:
                self.setfocus()

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_L:
                pyperclip.copy(self.toPlainText())
            elif event.key() == Qt.Key_E:
                self.export_script()
        else:
            super().keyPressEvent(event)

# Keyword Highlighter Class for the scripting textEdit
class KeywordHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keywords = ["click", "wait", "open", "show", "keyboard"]
        # Format for keywords
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(44, 122, 214))

        # Format for arguments after the keyword
        self.argument_format = QTextCharFormat()
        self.argument_format.setForeground(QColor(150, 75, 0))

    def highlightBlock(self, text):
        """Highlight only the first occurrence of a keyword per line."""
        for keyword in self.keywords:
            start = 0
            while start < len(text):
                start = text.find(keyword, start)
                if start == -1:
                    break  # No keyword found, move to next keyword
                # Find the end of the line
                end_of_line = text.find("\n", start)
                if end_of_line == -1:
                    end_of_line = len(text)

                # Apply keyword format to the first occurrence
                self.setFormat(start, len(keyword), self.keyword_format)
                # Apply argument format to the rest of the line after the first keyword
                arg_start = start + len(keyword) + 1
                if arg_start < end_of_line:
                    self.setFormat(arg_start, end_of_line - arg_start, self.argument_format)
                break  # Stop after the first occurrence per line
