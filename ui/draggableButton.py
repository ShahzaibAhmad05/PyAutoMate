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
from modules.interpreter import interpret

""" DraggableButton class """

class DraggableButton(QPushButton):
    def __init__(self, parent, scriptID):
        super().__init__(parent)

        self.parent = parent
        self.scriptID = scriptID
        self.dragging = False
        self.position = (0, 0)

        # setup button attributes using refresh
        self.refresh()

        # additional setup
        self.setObjectName("QPushButton")
        self.parent = parent

    def edit_script(self) -> None:
        """ allows the user to edit the script """
        add_button_window = AddButtonWindow(parent=self.parent, commands_list=self.code, 
                                      completion_signal=self.completion_signal,
                            existing_image=get_icon_path(self.iconID))
        self.parent.hide()

        if add_button_window.exec_() == QDialog.Accepted:

            # update the attributes of the current button
            self.iconID, self.code, self.completion_signal = add_button_window.get_input()
            # save the updated script
            save_script(self.id, self.code, self.iconID, self.completion_signal)
            self.refresh()

        self.parent.show()

    def deleteButton(self):
        if QMessageBox.question(self, 'PyAutoMate', 'Are you sure you want to delete this button?') == QMessageBox.Yes:
            delete_script(self.scriptID, self.iconID)
            i, j = self.parent().get_row_col_by_pos(self.position)
            self.parent().occupancies[i][j] = False
            self.hide()
        else:
            # place the button back
            self.parent().check_snap(self, self.position)

    def run_script(self):
        interpret(self.parent, commands=self.code, comp_signal=self.completion_signal)

    def refresh(self):
        """ refreshes the button's attributes from the saved script data """
        script_data = load_script(self.scriptID)        # load the script data
        self.code = script_data['code']
        self.iconID = script_data['iconID']
        self.completion_signal = script_data['completionSignal']

        self.updateIcon()

    def updateIcon(self):
        self.setIcon(QIcon(get_icon_path(self.iconID)))

    def mouseDoubleClickEvent(self, event: None) -> None:
        self.run_script()

    def mousePressEvent(self, event):
        if self.parent().is_small and event.button() == Qt.LeftButton:
            # wait for the mouse button to be released
            while mouse.is_pressed('left'): sleep_for(25)
            self.run_script()
        else:
            self.position = self.pos()
            self.dragging = True
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:  # Allow movement only if dragging is active and not snapped
            self.move(self.mapToParent(event.pos() - self.drag_start_position))

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            # Check if the button should snap
            self.parent().check_snap(self, self.position)

    def contextMenuEvent(self, event):
        if self.parent().is_small: return
        # initialize context menu
        menu = QMenu(self)

        # create options in the menu
        action1 = menu.addAction(add_spaces_for_context_menu("Run Script", ''))
        menu.addSeparator()
        action2 = menu.addAction(add_spaces_for_context_menu("Edit Script", ''))
        action3 = menu.addAction(add_spaces_for_context_menu(
            "Add Icon" if self.icon_to_set is None else 'Edit Icon'))
        action5 = None
        if self.iconID is not None:
            text_to_add = add_spaces_for_context_menu("Remove Icon", '')
            action5 = menu.addAction(text_to_add)
        menu.addSeparator()
        action6 = menu.addAction("Delete")

        context_menu_stylesheet(menu, self.parent)       # set stylesheet for context menu
        action = menu.exec_(self.mapToGlobal(event.pos()))  # run context menu
   
        if action == action1:
            self.run_script()

        elif action == action2:
            self.edit_script()
            
        elif action == action3:
            image_path, _ = QFileDialog.getOpenFileName(
                                parent=self,
                                caption="Select An Image",
                                filter="Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff *.svg);;All Files (*)",
                                options=QFileDialog.Options())
            if not os.path.exists(image_path): return       # make sure we have a valid path
            # remove the old image
            if os.path.exists(get_icon_path(self.iconID)): 
                os.remove(get_icon_path(self.iconID))

            # save the icon in the script
            shutil.copy(image_path, get_icon_path(self.scriptID))
            save_script(self.scriptID, self.code, self.scriptID, 
                        self.completion_signal)
            self.refresh()      # refresh to apply changes

        elif action5 and action == action5:
            # remove the icon from script file
            save_script(self.scriptID, self.code, None, self.completion_signal)
            self.refresh()
            
        elif action == action6:
            self.deleteButton()
# end of DraggableButton class