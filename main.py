""" All Imports """
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap
import logging
import os
import inspect
import pickle
from modules.functions import sleep_for
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
from modules.functions import save_script, delete_script, load_script, enable_dragging, generateRandomID
from ui.settings import Settings
from ui.scriptingDialog import ScriptingDialog
from modules.styling import (push_button_disabled_stylesheet, push_button_stylesheet,
                            context_menu_stylesheet, dialog_window_stylesheet)

pyautogui.FAILSAFE = False

# need a root app to get started
root_app = QApplication([])

# start of MainTool Class
class MainTool(QMainWindow):
    def __init__(self):
        super().__init__()

        # setting up the settings
        settings = get_settings()
        self.app_theme = settings['theme']
        self.app_grid = int(settings['grid'])
        self.app_size = int(settings['size'])
        self.font_size = int(self.app_size * 0.45)

        # Set up the main window and object variables
        self.setWindowTitle("PyAutoMate")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # setup behaviour control variables
        self.message_bad_grid_given = False
        self.is_small = True
        self.app_launched = False
        self.restricted = False
        self.prev_xy = None

        # initialize the grid variables of the app
        rows, cols = self.app_grid, self.app_grid + 2
        self.occupancies = [[False for _ in range(cols)] for _ in range(rows)]
        self.snap_positions = [[self.get_grid_xy(i, j) for j in range(cols)] for i in range(rows)]

        # setup background color
        self.background_color = (QColor(244, 244, 244) 
            if self.app_theme == 'light' else QColor(30, 30, 30))

        # initialize the user interface
        self.init_ui()
        enable_dragging(self)
        # Assistant control variables
        self.assistant_text_enabled = True
        self.floating_textbox = GlobalTextBox(self)


    def init_ui(self) -> None:
        """ Initialize the UI components of the main window """
        # setup logo button
        self.logo_button = QPushButton(self)
        self.logo_button.setIcon(QIcon(get_logo_path()))
        self.logo_button.setStyleSheet("QPushButton { border: none; }")
        self.logo_button.mouseDoubleClickEvent = self.open_tool
        self.logo_button.mousePressEvent = self.mousePressEvent
        self.logo_button.mouseMoveEvent = self.mouseMoveEvent
        self.place_button(self.logo_button, 0, 0)

        # setup app title
        self.app_title_label = QLabel("PyAutoMate", self)
        self.app_title_label.setStyleSheet(
            f" color: rgb(0, 131, 172); font-size: {self.font_size}px; "
            f" margin-top: {self.font_size // 12}; margin-left: {self.font_size // 4}; "
        )

        # add scripted buttons
        for script in os.listdir('scripts'):
            self.button = DraggableButton(self, scriptID=script.split('.')[0])
            push_button_stylesheet(self.button, self)
            self.place_button(self.button)

        # call open_tool() to shape the app
        self.open_tool(event=None, animate=False)
        # Move the logo and its label to appropriate position
        self.place_logo_and_title()
        
    def openSettings(self) -> None:
        """ creates an instance of Settings() which is a QDialog """
        self.settings_window = Settings(self)
        self.settings_window.show()
        self.hide()
        
        # check if OK button was pressed
        if self.settings_window.exec_() == QDialog.Accepted:
            self.settings_window.save_settings()
            # else statement is only for testing purposes during development
            if os.path.exists('PyAutoMate.exe'):
                os.startfile('PyAutoMate.exe')
                while True: sleep_for(500)      # wait for the other instance to close this one
            else: 
                # reaches here only if settings are opened in development environment
                sleep_for(1000)
                self.decoy_window.hide()
        self.show()

    def add_new_button(self):
        """ creates an instance of AddButtonWindow() which is a QDialog """
        scriptEditor = AddButtonWindow(self, commands_list=None,
                                            existing_image=None, completion_signal=False)
        scriptEditor.show()
        self.hide()     # hide main tool only after editor is shown

        if scriptEditor.exec_() == QDialog.Accepted:
            image_path, code, completion_signal = scriptEditor.get_input()
            scriptID = generateRandomID()
            iconID = None

            # save the icon if given
            if os.path.exists(image_path):
                iconID = generateRandomID()
                shutil.copy(image_path, iconID)

            save_script(scriptID, iconID, code, completion_signal)
            # show the button for this instance too
            self.button = DraggableButton(self, scriptID)
            push_button_stylesheet(self.button, self)
            self.place_button(self.button)

        self.show()

    def place_logo_and_title(self):
        # Properly places the logo and title
        x = (((self.app_size * self.app_grid + 
            ((self.app_size // 5) * self.app_grid)) // 2) - 
            (self.app_title_label.width() // 2) + (self.app_size // 3))
        y = self.logo_button.pos().y() + self.app_size // 5
        self.logo_button.setGeometry(x, y - self.app_size // 5, 
                                     self.logo_button.width(), 
                                     self.logo_button.height())
        self.app_title_label.setGeometry(x + self.logo_button.width(), y, 
                                         self.font_size * 6, int(self.font_size * 1.5))

    def open_tool(self, event=None, animate: bool=True):
        if self.is_small:
            if self.app_launched:
                self.prev_xy = [self.geometry().x(), self.geometry().y()]

            window_width = ((self.app_grid + 2) * (self.app_size + self.app_size // 10) + 
                self.app_size // 10)
            window_height = ((self.app_grid) * (self.app_size + self.app_size // 10) + 
                             (2 * self.app_size) // 5)
            target_geometry = QRect(
                pyautogui.size()[0] // 2 - window_width // 2 - self.app_size,
                pyautogui.size()[1] // 2 - window_height // 2 - self.app_size,
                window_width,
                window_height,
            )
            
            if animate:
                self.animate_transformation(target_geometry)
            else:
                self.setGeometry(target_geometry)
                self.app_launched = True

            # Properly Position the logo button
            self.place_logo_and_title()
        else:
            self.update_dimensions()
            self.place_button(self.logo_button, 0, 0)

        self.is_small = not self.is_small

    def animate_transformation(self, target_geometry):
        """ defines an animation for maximizing/minimizing the tool """
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(target_geometry)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def get_grid_xy(self, row=0, column=0):
        condition = row == 0 and column == 0
        padding = self.app_size // 10
        extra = 0 if condition else padding * 2
        return (padding + column * self.app_size + column * padding, 
                padding * 2 + row * self.app_size + row * padding + extra)

    def get_row_col_by_pos(self, position) -> tuple:
        """ 
        - Takes: a position calculated using pyautogui.position()
        - Returns: a tuple of row, column where the position leads to
        """
        for i in range(self.app_grid):
            for j in range(self.app_grid+2):
                if (position.x(), position.y()) == self.get_grid_xy(i, j):
                    return i, j
        QMessageBox.critical(self, 'PyAutoMate', 'An Unexpected Error Occured!')
        sys.exit(0)

    def get_number_of_buttons(self):
        number = 0
        for i in range(len(self.occupancies)):
            if self.occupancies[i][0] == True:
                number = i + 1
        return number

    def place_button(self, widget, row=-1, col=-1):
        def find_empty_space():
            for row in range(len(self.occupancies)):
                for col in range(len(self.occupancies[0])):
                    if (col == 0 and row != 0) or (col != 0 and row == 0): 
                        continue
                    elif self.occupancies[row][col] == False:
                        return row, col
            return -1, -1
        if row == -1 and col == -1:
            row, col = find_empty_space()
            if row == -1 and col == -1:
                if not self.message_bad_grid_given:
                    QMessageBox.critical(self, 'PyAutoMate',
                                         'Error placing widgets: button placement cancelled, '
                                        'try increasing the grid from PyController.exe')
                    self.message_bad_grid_given = True
                widget.setGeometry(0, 0, 0, 0)
                return

        condition = row == 0 and col == 0
        extra = 0 if condition else self.app_size // 5
        x, y = self.get_grid_xy(row, col)
        widget.setGeometry(x, y, self.app_size, self.app_size)
        widget.setIconSize(QSize(widget.size().width() - extra, 
                                 widget.size().height() - extra))
        self.occupancies[row][col] = True

    def update_dimensions(self, from_button: bool=False) -> None:
        number_of_buttons = self.get_number_of_buttons()
        width = self.app_size + self.app_size // 5
        height = 10 + number_of_buttons * self.app_size + self.app_size // 5 + number_of_buttons * 5

        if self.prev_xy and not from_button:
            x, y = self.prev_xy
        else:
            x = pyautogui.size()[0] - width - self.app_size // 5
            y = pyautogui.size()[1] // 2 - height // 2 - self.app_size

        target_geometry = QRect(x, y, width, height)
        self.animate_transformation(target_geometry)

    def check_snap(self, button, initial_position):
        """
        Check if the button is near the snap spot.
        If it is, snap it to the spot.
        """
        for row in range(len(self.occupancies)):
            if self.occupancies[row][0] == False:
                width = self.app_size // 10
                height = width * 2 + row * self.app_size + row * width + width * 2
                snap_position = QPoint(width, height)

        button_position = button.pos()
        # Define a threshold for snapping
        threshold = int(self.app_size * 0.6)

        # Calculate the distance between the button and the snap spot
        def check_positions(self):
            for i in range(self.app_grid):
                if i == 0: continue
                for j in range(self.app_grid+2):
                    point = QPoint(self.snap_positions[i][j][0], self.snap_positions[i][j][1])
                    distance = QPoint(button_position - point).manhattanLength()

                    if self.occupancies[i][j] == True: continue
                    elif distance < threshold:
                        self.occupancies[i][j] = True
                        return point
            return

        snap_position = check_positions(self)
        # i, j is the initial row x column
        i, j = self.get_row_col_by_pos(initial_position)
        if snap_position:
            self.occupancies[i][j] = False
            button.move(snap_position)
        else:
            self.occupancies[i][j] = True
            self.place_button(button, row=i, col=j)

    def paintEvent(self, event=None):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Create rounded rectangle using QPainter
        painter.setBrush(self.background_color)
        painter.setPen(Qt.NoPen)  # Remove the border
        painter.drawRoundedRect(self.rect(), self.app_size // 5, self.app_size // 5)
        painter.end()

    def contextMenuEvent(self, event):
        """ Shows a general context menu for the app """
        # initialize the main tool menu
        menu = QMenu(self)
        action2 = menu.addAction('Open Tool' if self.is_small else 'Minimize Tool')

        if not self.is_small:
            menu.addSeparator()
            new_sub_menu = menu.addMenu('New')

            action4 = new_sub_menu.addAction(add_spaces_for_context_menu('Script', ''))
            assistant_sub_menu = menu.addMenu('Assistant')

            action6 = assistant_sub_menu.addAction(add_spaces_for_context_menu(("✔️" if self.assistant_text_enabled else "❌") + " Text", ''))

            action3 = menu.addAction(add_spaces_for_context_menu("Settings", ''))
            menu.addSeparator()

            actione = menu.addAction(add_spaces_for_context_menu("Exit", ''))
            context_menu_stylesheet(new_sub_menu, self)
            context_menu_stylesheet(assistant_sub_menu, self)

        context_menu_stylesheet(menu, self)

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action is None: return
        elif action == action2:
            self.open_tool()

        elif not self.is_small and action == action3:
            self.openSettings()

        elif not self.is_small and action == action4:
            self.add_new_button()

        elif not self.is_small and action == actione:
            self.floating_textbox.hide(animation=False)
            if QMessageBox.question(self, 'PyAutoMate', 
                                    'Are you sure you want to exit?') == QMessageBox.Yes:
                QApplication.quit()

        elif not self.is_small and action == action6:
            self.assistant_text_enabled = not self.assistant_text_enabled

    def show(self):
        super().show()
        self.restricted = False

    def hide(self):
        self.restricted = True
        super().hide()
# end of MainTool class

        # -- TODO: I was working here
# start of ScriptOption class
class ScriptOption(QDialog):
    def __init__(self, parent, ok_button_name: str, functions: dict[str, Callable]=None, 
                 radios: list[str]=None, inputs: list[str]=None):
        super().__init__()

        self.parent = parent
        self.setWindowTitle('Select An Option')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setFixedWidth(self.parent.app_size * 7)
        title_bar_widget = dialog_window_stylesheet(self)
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
# end of ScriptOption class

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
# end of KeywordHighlighter class

""" AddButtonWindow Class """
class AddButtonWindow(QDialog):
    def __init__(self, parent, commands_list: list[list], existing_image: str, completion_signal):
        super().__init__(parent)

        self.parent = parent
        self.setWindowTitle("Script Editor")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setFixedWidth(int(pyautogui.size()[0] * 0.75))
        self.parent = parent
        self.commands_list = []
        title_bar_widget = dialog_window_stylesheet(self, self.parent)

        # Layout for the second window
        scripting_buttons_layout = QVBoxLayout()
        main_layout = QVBoxLayout()
        scripting_buttons = {'Clicks Recorder': self.action_recorder, 'Click': self.mouse_click, 'Wait For': self.wait_for,
                             'Open File/Link': self.open_file_or_link, '   Type Write/Shortcut Keys   ': self.keyboard_op,
                             'Show Window': self.window_shower}
        # create all the required buttons in scripting buttons dict
        self.button_references = []
        for key, value in scripting_buttons.items():
            self.button = QPushButton(key, self)
            self.button_references.append(self.button)
            self.button.clicked.connect(value)
            scripting_buttons_layout.addWidget(self.button)
            self.button.setObjectName("QPushButton")
        
        spacer = QLabel(self)
        scripting_buttons_layout.addWidget(spacer)

        # define a scroll wheel zooming event for the input field
        def wheel_event_for_textbox(text_edit, event):
            if event.modifiers() == Qt.ControlModifier:  # Check if Ctrl is pressed
                current_font = text_edit.font()
                current_size = current_font.pointSizeF()

                if event.angleDelta().y() > 0:  # Scroll up (Increase font size)
                    new_size = min(30.0, current_size + 2)
                else:  # Scroll down (Decrease font size)
                    new_size = max(10.0, current_size - 2)  # Prevent zero or negative size
                current_font.setPointSizeF(new_size)
                text_edit.setFont(current_font)  # Set font directly
                text_edit.update()
                event.accept()  # Prevent default scrolling
            else:
                QTextEdit.wheelEvent(text_edit, event)  # Normal scrolling

        self.input_field = CustomTextEdit(self.parent)
        font = self.input_field.font()
        font.setPointSize(14)
        self.input_field.setFont(font)
        self.input_field.setProperty("customFontSize", 14)  # Store initial font size
        self.input_field.wheelEvent = lambda event: wheel_event_for_textbox(self.input_field, event)

        if commands_list:
            for command in commands_list:
                for word in command:
                    index = command.index(word)
                    if type(word) != str:
                        command[index] = str(command[index])
                command = ' '.join(command)
                self.input_field.append(command)
        main_layout.addWidget(self.input_field)

        self.select_icon_button = QPushButton("Select Icon", self)
        self.select_icon_button.clicked.connect(self.select_icon)
        main_layout.addWidget(self.select_icon_button)
        self.select_icon_button.setObjectName("QPushButton")
            
        # label to show the selected icon's path
        if existing_image is None:
            self.file_path = ''
            self.icon_label = QLabel("Icon: Not Selected", self)
        else:
            self.file_path = existing_image
            self.icon_label = QLabel(f"Icon: Selected")
        main_layout.addWidget(self.icon_label)
        self.button.setObjectName("QPushButton")

        self.includes_icon = QCheckBox('Include Icon', self)
        self.includes_icon.setChecked(True if self.file_path else False)
        self.set_icon_or_not()
        self.includes_icon.setStyleSheet(" margin-top: 15px;")
        self.includes_icon.toggled.connect(self.set_icon_or_not)
        main_layout.addWidget(self.includes_icon)
        self.completion_check = QCheckBox('Include Completion Signal', self)
        self.completion_check.setChecked(completion_signal)
        main_layout.addWidget(self.completion_check)

        # create ok and cancel buttons using the same logic as above
        scripting_buttons = {"Cancel": self.reject, "OK": self.on_ok}
        ok_cancel_layout = QHBoxLayout()
        ok_cancel_layout.addWidget(QLabel(self))
        ok_cancel_layout.addWidget(QLabel(self))
        for key, value in scripting_buttons.items():
            self.button = QPushButton(key, self)
            self.button.clicked.connect(value)
            ok_cancel_layout.addWidget(self.button)
            self.button.setObjectName("QPushButton")
        ok_cancel_widget = QWidget(self)
        ok_cancel_widget.setLayout(ok_cancel_layout)
        main_layout.addWidget(spacer)
        main_layout.addWidget(spacer)
        main_layout.addWidget(spacer)
        main_layout.addWidget(spacer)
        main_layout.addWidget(ok_cancel_widget)

        main_widget = QWidget(self)
        main_widget.setLayout(main_layout)
        sidebar_widget = QWidget(self)
        sidebar_widget.setLayout(scripting_buttons_layout)
        sidebar_widget.setStyleSheet(" margin: 0; ")
        horizontal_layout = QHBoxLayout()

        horizontal_layout.addWidget(sidebar_widget)
        horizontal_layout.addWidget(main_widget)
        horizontal_widget = QWidget()
        horizontal_widget.setLayout(horizontal_layout)
        window_widget_parent = QVBoxLayout()
        window_widget_parent.addWidget(title_bar_widget)
        window_widget_parent.addWidget(horizontal_widget)
        self.setLayout(window_widget_parent)
        self.input_field.setFocus()
        enable_dragging(self)

        # center the window on the screen
        self.adjustSize()
        self.move(pyautogui.size()[0] // 2 - self.width() // 2, pyautogui.size()[1] // 2 - self.height() // 2)
        
    def set_icon_or_not(self):
        if self.includes_icon.isChecked():
            self.select_icon_button.setEnabled(True)
            push_button_stylesheet(self.select_icon_button, self.parent)
            self.icon_label.setText(f'Icon: Selected' if self.file_path else 'Icon: Not Selected')
        else:
            self.select_icon_button.setEnabled(False)
            push_button_disabled_stylesheet(self.select_icon_button, self.parent)
            self.icon_label.setText('Icon: Disabled')

    def action_recorder(self):
        """ the best of all script writer buttons, records clicks, double clicks automatically, with time intervals too """
        # self.button_references[0].setEnabled(False)
        option_window = ScriptOption(self.parent, "Start Recording", radios=['Add Time Intervals', 'Ignore Time Intervals'])

        if option_window.exec_() == QDialog.Accepted:
            QMessageBox.information(self, 'PyAutoMate', 'Usage:\n  l -> left click\n'
                                    '  r -> right click\n  d -> double click')
            include_time = True if option_window.get_selected_option().startswith('Add') else False
            current_position = self.pos()
            self.move(pyautogui.size()[0], 0)
            main_loop_flag = True

            def write_script_for_action(start_time, stop_key: str, click_type: str, func_to_run: Callable):
                if include_time:
                    self.input_field.insertPlainText(f'wait time {round(time.time() - start_time + 0.6, 0)}\n')
                while keyboard.is_pressed(stop_key): sleep_for(25)
                location = pyautogui.position()
                self.input_field.insertPlainText(f'click {click_type} coord {location.x} {location.y}\n')
                func_to_run(location.x, location.y)

            while main_loop_flag:
                start_time = time.time()
                while True:
                    if keyboard.is_pressed('ctrl+c'):
                        main_loop_flag = False
                        break
                    elif keyboard.is_pressed('d'):
                        write_script_for_action(start_time, 'd', 'double', pyautogui.doubleClick)
                        break
                    elif keyboard.is_pressed('l'):
                        write_script_for_action(start_time, 'l', 'left', pyautogui.leftClick)
                        break
                    elif keyboard.is_pressed('r'):
                        write_script_for_action(start_time, 'r', 'right', pyautogui.rightClick)
                        break
                    else:
                        sleep_for(25)

            self.move(current_position.x(), current_position.y())
        self.input_field.setFocus()

    def mouse_click(self):
        current_position = self.pos()
        # helper functions capture and get free path
        def capture(button_type):
            # saves the current position to call it back later
            current_position = option_window.pos()
            option_window.move(pyautogui.size()[0], 0)
            if button_type == 'double':
                button_to_wait = 'left'
            else: button_to_wait = button_type
            while not mouse.is_pressed(button_to_wait): sleep_for(25)
            while mouse.is_pressed(button_to_wait): sleep_for(25)
            position = pyautogui.position()
            # calls the dialog back to the last saved position
            option_window.move(current_position.x(), current_position.y())
            if option_window.get_selected_option().endswith('Coordinates'):
                self.input_field.insertPlainText(f'click {button_type} coord {position.x} {position.y}\n')
            elif option_window.get_selected_option().endswith('Image'):
                id = save_screenshot(position)
                self.input_field.insertPlainText(f'click {button_type} img 10 {id}\n')

        def save_screenshot(position: tuple) -> int:
            """ saves the 16x16 screenshot of the given location, and returns the save path """
            shot = pyautogui.screenshot(region=(position.x - 8, position.y - 8, 16, 16))
            loopFlag = True
            id = generateRandomID()

            shot.save(get_icon_path(id))
            return id

        self.move(pyautogui.size()[0], 0)
        functions = {'Left Click': lambda: capture("left"), 
                     'Right Click': lambda: capture("right"), 
                     'Double Click': lambda: capture("double")}
        option_window = ScriptOption("Back", functions, ['Click by Coordinates', 'Click by Image'])
        option_window.exec_()

        self.move(current_position.x(), current_position.y())
        self.input_field.setFocus()

    def open_file_or_link(self: QWidget) -> None:
        def open_file():
            file_path, _ = QFileDialog.getOpenFileName(parent=self, caption="Select File", 
                                                        filter="All Files (*)", 
                                                        options=QFileDialog.Options())
            if file_path:
                self.input_field.insertPlainText(f'open file {file_path}\n')
        def open_folder():
            folder_path = QFileDialog.getExistingDirectory(parent=self, caption="Select Folder", 
                                                           options=QFileDialog.Options())
            if folder_path:
                self.input_field.insertPlainText(f'open file {folder_path}\n')
        def open_link():
            text, ok = QInputDialog.getText(self, "Open Website Link", "Paste Website Link Here:", flags=Qt.Tool)
            if ok and text:  # If user clicks OK and input is not empty
                self.input_field.insertPlainText(f'open link {text}\n')

        context_menu = QMenu(self)
        context_menu_stylesheet(context_menu, self.parent)
        action1 = context_menu.addAction("Select File")
        text_to_add = add_spaces_for_context_menu("Select Folder", '')
        action2 = context_menu.addAction(text_to_add)
        action3 = context_menu.addAction("Select Link")
        action1.triggered.connect(open_file)
        action2.triggered.connect(open_folder)
        action3.triggered.connect(open_link)
        context_menu.exec_(QCursor.pos())
        self.input_field.setFocus()

    def wait_for(self):
        def copy_mouse_button():
            while True:
                if mouse.is_pressed('left'):
                    option_window.get_input_values()[0].setText("left")
                    break
                elif mouse.is_pressed('right'):
                    option_window.get_input_values()[0].setText("right")
                    break
                elif mouse.is_pressed('middle'):
                    option_window.get_input_values()[0].setText("middle")
                    break
                else:
                    sleep_for(25)
        def copy_keyboard_button():
            while True:
                event = keyboard.read_event(suppress=True)
                if event.event_type == keyboard.KEY_DOWN:
                    option_window.get_input_values()[0].setText(event.name)
                    break
                else: sleep_for(25)

        option_window = ScriptOption("OK", radios=['Keyboard', 'Mouse', 'Seconds'], 
                                     inputs=['Button (if Keyboard or Mouse is selected): ', 
                                             'Wait For Seconds (if Seconds is selected): '],
                                    functions={'Copy Mouse Button': copy_mouse_button, 
                                               'Copy Keyboard Button': copy_keyboard_button})
        if option_window.exec_() == QDialog.Accepted:
            # wait time_img_key opt_keyboard_mouse float_or_button
            entered_values = option_window.get_input_values()
            if option_window.get_selected_option() in ['Keyboard', 'Mouse'] and entered_values[0].text():
                if option_window.get_selected_option() == 'Keyboard':
                    self.input_field.insertPlainText(f'wait key keyboard {entered_values[0].text()}')
                elif option_window.get_selected_option() == 'Mouse':
                    self.input_field.insertPlainText(f'wait key mouse {entered_values[0].text()}')
            elif option_window.get_selected_option() == 'Seconds' and entered_values[1].text():
                self.input_field.insertPlainText(f'wait time {entered_values[1].text()}')
        self.input_field.setFocus()

    def keyboard_op(self):
        option_window = ScriptOption("OK", radios=['Type this (text)', 'Press these (shortcut keys)'], 
                                     inputs=['Text or Buttons'])

        if option_window.exec_() and option_window.get_input_values()[0].text():
            to_type = option_window.get_input_values()[0].text()
            if option_window.get_selected_option().startswith('Type'): type_or_press = 'type'
            elif option_window.get_selected_option().startswith('Press'): type_or_press = 'press'
            self.input_field.insertPlainText(f'keyboard {type_or_press} {to_type}')
        self.input_field.setFocus()

    def window_shower(self):
        def capture_window_title():
            while not mouse.is_pressed('left'): sleep_for(25)
            sleep_for(750) # waits for a second before claiming the active window
            window = getActiveWindow()
            option_window.get_input_values()[0].setText(window.title)

        option_window = ScriptOption("OK", inputs=['Window Title: '], 
                                     functions={'Capture Next Window\'s Title': capture_window_title})
        if option_window.exec_() and option_window.get_input_values()[0].text():
            self.input_field.insertPlainText(f'show {option_window.get_input_values()[0].text()}')
        self.input_field.setFocus()

    def on_ok(self) -> None:
        if not self.input_field.toPlainText():
            QMessageBox.critical(self, 'PyAutoMate', 'The compilation cannot be done because the script is empty.')
        else:
            script = self.input_field.toPlainText().splitlines()
            for line in script:
                line = line.split()
                self.commands_list.append(line)

            # TODO: Debugger implementation required here.

            approval = True
            if approval:
                if not self.file_path and self.includes_icon.isChecked() and QMessageBox.critical(self, 'PyAutoMate', 
                    'The compilation cannot be done because no icon was chosen for the button. '
                    'Uncheck \'Include Icon\' to get rid of this error.'):
                    self.commands_list = []
                else:
                    self.accept()
            else:
                QMessageBox.critical(self, 'PyAutoMate', 
                                     'Incorrect syntax, the script could not be compiled.')
                self.commands_list = []

    def get_input(self):
        """ Returns the input text """
        if not self.includes_icon.isChecked():
            self.file_path = ''
        return [self.file_path, self.commands_list, self.completion_check.isChecked()]

    def select_icon(self):
        """ Open file dialog to select an image and display the file path """
        new_file_path, _ = QFileDialog.getOpenFileName(
                                parent=self,
                                caption="Select An Image",
                                filter="Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff *.svg);;All Files (*)",
                                options=QFileDialog.Options())
        if new_file_path:
            self.file_path = new_file_path
            self.icon_label.setText(f"Selected Image: {os.path.basename(self.file_path)}")

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
        interpreter(self.parent, commands=self.code, comp_signal=self.completion_signal)

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

def add_spaces_for_context_menu(text: str, shortcut_key: str, space_rule: int=22) -> str:
    """
    Adds the required spaces to the text of a context menu option.

    Args:
        text (str): The text which the button is going to hold.
        shortcut_key (str): The shortcut key of the button in the app.
        space_rule (int): Defines the width of the option.
    Returns:
        str: The text to add to the context menu option.
    """
    space_rule = 22
    for _ in range(space_rule - len(text)):
        text += ' '
    for _ in range(space_rule // 4 - len(shortcut_key)):
        text += ' '
    text += shortcut_key
    return text



""" interpreter function """

def interpreter(parent, commands: list[list], comp_signal: bool=False) -> None:
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
    close_other_instances()
    root_app.setWindowIcon(QIcon(get_logo_path()))

    main_tool = MainTool()
    main_tool.show() # finally, show the main tool

    root_app.exec_()   # should never exit from here
    sys.exit(1)

if __name__ == "__main__":
    main()