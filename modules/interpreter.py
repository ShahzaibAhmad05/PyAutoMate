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
from modules.styling import dialog_window_stylesheet, context_menu_stylesheet, push_button_stylesheet, push_button_disabled_stylesheet
from modules.utils import enable_dragging, add_spaces_for_context_menu, generateRandomID, save_script, delete_script, load_script
from ui.toggleSwitch import ToggleSwitch
from ui.customTextEdit import CustomTextEdit
from ui.scriptOption import ScriptOption
from modules.getters import get_icon_path
from ui.addButtonWindow import AddButtonWindow


""" interpreter function """

def interpret(parent, commands: list[list], comp_signal: bool=False) -> None:
    """
    takes in a list of interpreter readable commands with the proper format to execute them.
    Command[0]: the type of the command
    Command[1]: the specification of the type

    param: parent is a widget on which the dialogs would be set
    param: commands is a list of lists, where each list represents a command
    param: variables (dict)
    param: comp_signal if true, provides a signal on completion of the script, false by default
    param: dialogs_parent (ptr) points to the window hosting the dialogs, i.e. small tool

    """
    parent.hide()
    sleep_for(100)

    for command in commands:

        # if command is empty or just a \n
        if not command: pass

        # for mouse clicks
        elif command[0] == 'click':

            # the click type, left, right, or double
            if command[1] == 1: click_function = pyautogui.leftClick
            elif command[1] == 2: click_function = pyautogui.rightClick
            elif command[1] == 3: click_function = pyautogui.doubleClick

            # click by coordinates
            if command[2] == 'coord':
                x = int(command[3])
                y = int(command[4])
                click_function(x, y)

            # click by image, also requires timeout
            elif command[2] == 'img':
                timeout = command[3]
                # load the image
                image_path = 'images/' + command[4] + '.png'
                with open(image_path, 'rb') as file:
                    image_data = file.read()

                x, y = find_image_location(image_data, timeout)
                if x and y:
                    click_function(x, y)
                else:
                    QMessageBox.critical(parent, 'PyAutoMate', f'The required image was not Found within {timeout} seconds')
                    break

        # for opening
        elif command[0] == 'open':

            # opening local files
            if command[1] == 'file':
                file_path = ''.join(command[2:])
                if os.path.exists(file_path):
                    os.startfile(file_path)
                else:
                    QMessageBox.critical(parent, 'PyAutoMate', f'{file_path} does not exist')

            # opening websites on default browser
            elif command[1] == 'link':
                link = command[2]
                webbrowser.open(link)

        # for waiting
        elif command[0] == 'wait':

            # for waiting for a specified time
            if command[1] == 'time':
                sleep_time = int(command[2]) * 1000
                sleep_for(sleep_time)

            # for waiting for a specific image to appear
            elif command[1] == 'img':
                timeout = int(command[2])
                image_path = 'images/' + command[3] + '.png'
                with open(image_path, 'rb') as file:
                    image_data = file.read()

                if not find_image_location(image_data, timeout):
                    QMessageBox.critical(parent, 'PyAutoMate', f'The required image was not Found within {timeout} seconds')
                    break

            # for waiting for a button press
            elif command[1] == 'key':
                button = command[3]
                while not keyboard.is_pressed(button): sleep_for(25)
                while keyboard.is_pressed(button): sleep_for(25)

            # for waiting for a mouse press
            elif command[1] == 'click':
                button = command[3]
                while not mouse.is_pressed(button): sleep_for(25)
                while mouse.is_pressed(button): sleep_for(25)

        # for doing some keyboard type action
        elif command[0] == 'key':

            # for typing
            if command[1] == 'type':
                content = command[2]
                pyautogui.typewrite(content, interval=0.005)

            # for pressing hotkeys
            elif command[1] == 'press':
                button = command[2].split('+')   # assuming command[2] is a list
                pyautogui.hotkey(button)
                sleep_for(500)

        # for showing a window
        elif command[0] == 'show':
            window_title = command[1]
            show_window(window_title, parent)

    # optionally provide a completion signal
    if comp_signal:
        QMessageBox.information(parent, 'PyAutoMate', f'Script was executed successfully')

    parent.show()

""" interpreter helper functions """

def find_image_location(binary_data: str, timeout: float) -> tuple:
    """
    helper function for interpreter to find images on the screen, 
    confidence=0.99 by default. Returns x and y coordinates of 
    the found image location, if not found, returns a tuple of none, none
    """
    image = Image.open(BytesIO(binary_data))
    start_time = time.time()
    while True:
        try:
            location = pyautogui.locateOnScreen(image, confidence=0.99)
            if location:
                return location.left, location.top
        except pyautogui.ImageNotFoundException:
            if time.time() - start_time > timeout:
                return None, None

def show_window(window_title: str, parent, timeout: int=0) -> None:
    """ activates the running window with the given title """
    start_time = time.time()
    while True:
        windows = getWindowsWithTitle(window_title)
        if windows:
            win = windows[0]
            win.activate()
            win.maximize()
            break
        elif time.time() - start_time > timeout:
            QMessageBox.critical(parent, 'PyAutoMate', f'Window with title {window_title} was not found')
            break
