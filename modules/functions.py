import json
import os
from .getters import get_script_path, get_icon_path
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap
import logging
import os
import inspect
import pickle
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

def save_script(scriptID: int | str, iconID: int | str, code: list, completion_signal: bool) -> None:
    """ saves a script to its corresponding JSON file """
    script_data = {
        "scriptID": scriptID,
        "iconID": iconID,
        "code": code,
        "completionSignal": completion_signal
    }
    with open(get_script_path(scriptID), 'w') as file:
        json.dump(script_data, file)

def delete_script(scriptID: int | str, iconID: int | str) -> None:
    """ removes a script JSON file """
    os.remove(get_icon_path(iconID))
    os.remove(get_script_path(scriptID))

def load_script(scriptID: int | str) -> dict:
    """ loads a script from its corresponding JSON file """
    with open(get_script_path(scriptID), 'r') as file:
        script_data = json.load(file)
    return script_data

def enable_dragging(widget):
    widget.is_dragging = False
    widget.drag_position = QPoint()

    def mousePressEvent(event):
        if event.button() == Qt.LeftButton:
            widget.is_dragging = True
            widget.drag_position = event.globalPos() - widget.pos()

    def mouseMoveEvent(event):
        if widget.is_dragging and event.buttons() == Qt.LeftButton:
            widget.move(event.globalPos() - widget.drag_position)

    def mouseReleaseEvent(event):
        if widget.is_dragging:
            widget.is_dragging = False
            x = max(0, min(widget.x(), pyautogui.size()[0] - widget.width()))
            y = max(0, min(widget.y(), pyautogui.size()[1] - widget.height()))
            widget.move(x, y)
            event.accept()

    widget.mousePressEvent = mousePressEvent
    widget.mouseMoveEvent = mouseMoveEvent
    widget.mouseReleaseEvent = mouseReleaseEvent

def generateRandomID() -> int:
    """ generates a random unused id """
    while True:
        id = random.randint(100000, 999999)
        if (not os.path.exists(get_icon_path(id)) and
            not os.path.exists(get_script_path(id))):
            return id
        
def sleep_for(sleep_time: int) -> None:
    """ 
    Calls a sleep event without blocking the app's loop.
    Args:
        sleep_time (int): requires time given in ms.
    """
    loop = QEventLoop()
    QTimer.singleShot(sleep_time, loop.quit)    # assuming sleep_time is in ms
    loop.exec_()