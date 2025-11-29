import psutil, sys, os
from PyQt5.QtWidgets import (QPushButton,
                            QDialog, QMessageBox, QVBoxLayout,
                            QTextEdit, QFileDialog, QRadioButton,
                            QButtonGroup, QMenu, QInputDialog, QLineEdit,
                            QCheckBox, QSpinBox)
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
from modules.styling import dialog_window_stylesheet
from modules.utils import enable_dragging
from ui.toggleSwitch import ToggleSwitch

def close_other_instances():
    """ no args, closes all the other instances of the current process """
    current_process = psutil.Process(os.getpid())
    current_name = current_process.name()
    # Check all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == current_name and proc.info['pid'] != current_process.pid:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except TimeoutError:
                QMessageBox.critical(None, 'PyAutoMate', 'An unexpected error occured. '
                        'Please contact the developer if the issue persists.')
                sys.exit(1)

def sleep_for(sleep_time: int) -> None:
    """ 
    Calls a sleep event without blocking the app's loop.
    Args:
        sleep_time (int): requires time given in ms.
    """
    loop = QEventLoop()
    QTimer.singleShot(sleep_time, loop.quit)    # assuming sleep_time is in ms
    loop.exec_()
