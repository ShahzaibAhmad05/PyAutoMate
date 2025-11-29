""" All Imports """
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap
import logging
import os
import inspect
import pickle
from modules.sysUtils import sleep_for, close_other_instances
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
# self-defined functions
from modules.getters import get_settings, get_logo_path, get_icon_path, get_script_path
from modules.utils import save_script, delete_script, load_script, enable_dragging, generateRandomID, add_spaces_for_context_menu
from ui.settings import Settings
from ui.scriptingDialog import ScriptingDialog
from ui.scriptOption import ScriptOption
from ui.customTextEdit import CustomTextEdit
from ui.addButtonWindow import AddButtonWindow
from ui.draggableButton import DraggableButton
from modules.styling import (push_button_disabled_stylesheet, push_button_stylesheet,
                            context_menu_stylesheet, dialog_window_stylesheet)
from mainTool import MainTool

pyautogui.FAILSAFE = False

""" Program Starts From Here After Imports """

def main():
    # check for any missing files and stylesheets
    required_files = ['settings.json']
    required_stylesheets = [
        'STD_button.css', 'STD_context_menu.css', 'STD_decoy.css', 'STD_dialog.css',
        'STL_context_menu.css', 'STL_decoy.css', 'STL_dialog.css', 'STF_toggle.css',
        'STN_toggle.css', 'STL_button_disabled.css', 'STD_button_disabled.css'
    ]
    missing_files = [f for f in required_files + [os.path.join('stylesheets', s) 
                        for s in required_stylesheets] if not os.path.exists(f)]

    if missing_files:
        QMessageBox.critical(None, 'PyAutoMate', 'Some required files are missing. Reinstalling the program might fix this problem.')
        sys.exit(1)

    # create the dirs if not exist
    os.makedirs('images', exist_ok=True)
    os.makedirs('scripts', exist_ok=True)

    # create the app root
    root_app = QApplication([])
    close_other_instances()
    root_app.setWindowIcon(QIcon(get_logo_path()))

    main_tool = MainTool()
    main_tool.show() # finally, show the main tool

    root_app.exec_()   # should never exit from here
    sys.exit(1)

if __name__ == "__main__":
    main()