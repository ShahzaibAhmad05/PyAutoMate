""" All Immediate Necessary Imports """
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap
import logging
import os
import inspect
import pickle
from Universal import sleep_for
from Assistant import GlobalTextBox
import threading

# need a root app to get started
root_app = QApplication([])

# start of DecoyWindow class
class DecoyWindow(QMainWindow):
    def __init__(self, text) -> None:
        """ 
        Creates a decoy window with a logo and some text alongside it.
        Use set_text() method to change the text on the window.
        
        Args:
            text (str): text to show on the decoy window.
        """
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SplashScreen)

        # Logo
        with open('settings.bin', 'rb') as file:
            data = pickle.load(file)
            app_size = data['app size']
            app_theme = data['theme']
        with open('logo.png', 'rb') as file:
            app_logo = file.read()
        self.logo_label = QLabel()
        pixmap = QPixmap()
        if not pixmap.loadFromData(app_logo):
            raise ValueError('Could not load pixmap for app logo in settings')
        self.logo_label.setPixmap(pixmap.scaled(app_size, app_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # set the screen size
        screen = self.screen().geometry()
        screen_width, screen_height = screen.width(), screen.height()

        # set the stylesheet of the window
        style_sheet_file = 'stylesheets/STD_decoy.css' if app_theme == 'dark' else 'stylesheets/STL_decoy.css'
        with open(style_sheet_file, 'r') as file:
            self.setStyleSheet(file.read())

        # Text
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignVCenter)
        self.label.setStyleSheet(" font-size: 18px; ")

        # Main widget & layout
        central_widget = QWidget(self)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(25, 0, 25, 0)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Add widgets to layout
        layout.addWidget(self.logo_label)
        layout.addWidget(self.label)
        self.setCentralWidget(central_widget)
        self.move(screen_width // 2 - self.width() // 4,
                  screen_height // 2 - self.height() // 4)

    def set_text(self, text) -> None:
        """ method used to change the text on the label """
        self.label.setText(text)
        sleep_for(25)

# create the loading window
loading_window = DecoyWindow('Importing module: time')
loading_window.show()
# start the imports
import time
start_time = time.time()
loading_window.set_text('Importing module: sys')
import sys
loading_window.set_text('Importing module: pyautogui')
import pyautogui
pyautogui.FAILSAFE = False
loading_window.set_text('Importing module: keyboard')
import keyboard
loading_window.set_text('Importing module: mouse')
import mouse
loading_window.set_text('Importing module: callable')
from typing import Callable
loading_window.set_text('Importing module: pyperclip')
import pyperclip
loading_window.set_text('Importing module: BytesIO')
from io import BytesIO
loading_window.set_text('Importing module: random')
import random
loading_window.set_text('Importing module: Image')
from PIL import Image
loading_window.set_text('Importing module: webbrowser')
import webbrowser
loading_window.set_text('Importing module: psutil')
import psutil
loading_window.set_text('Importing module: pygetwindow')
from pygetwindow import getActiveWindow, getWindowsWithTitle
loading_window.set_text('Importing module: PyQt5')
from PyQt5.QtWidgets import (QPushButton,
                            QDialog, QMessageBox, QVBoxLayout,
                            QTextEdit, QFileDialog, QRadioButton,
                            QButtonGroup, QMenu, QInputDialog, QLineEdit,
                            QCheckBox, QSpinBox)
from PyQt5.QtCore import QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QTextCharFormat, QSyntaxHighlighter, QColor, QPainter, QCursor, QFont
loading_window.set_text('Defining local modules...')

# start of MainTool Class
class MainTool(QMainWindow):
    def __init__(self):
        super().__init__()

        self.app_theme = app_theme
        
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
        rows, cols = app_grid, app_grid + 2
        self.occupancies = [[False for _ in range(cols)] for _ in range(rows)]
        self.snap_positions = [[self.get_grid_xy(i, j) for j in range(cols)] for i in range(rows)]
        # setup background color
        self.background_color = QColor(244, 244, 244) if app_theme == 'light' else QColor(30, 30, 30)

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
        self.logo_button.setIcon(binary_to_qicon(app_logo))
        self.logo_button.setStyleSheet("QPushButton { border: none; }")
        self.logo_button.mouseDoubleClickEvent = self.open_tool
        self.logo_button.mousePressEvent = self.mousePressEvent
        self.logo_button.mouseMoveEvent = self.mouseMoveEvent
        self.place_button(self.logo_button, 0, 0)

        # setup app title
        self.app_title_label = QLabel("PyAutoMate", self)
        font_size = int(app_size * 0.45)
        self.font_size = font_size
        self.app_title_label.setStyleSheet(
            f" color: rgb(0, 131, 172); font-size: {font_size}px; "
            f" margin-top: {font_size // 12}; margin-left: {font_size // 4}; "
        )

        # add scripted buttons
        for script in app_code:
            if 0 < script[0] < 1000000:
                self.button = DraggableButton(self, script[0], script[2], script[1], script[3])
                push_button_stylesheet(self.button)
                self.place_button(self.button)
        # call open_tool() to shape the app
        self.open_tool(event=None, animate=False)

        # Move the logo and its label to appropriate position
        self.place_logo_and_title()
        

    def open_settings(self) -> None:
        """ creates an instance of Settings() which is a QDialog """
        self.settings_window = Settings()
        self.settings_window.show()
        self.restricted = True
        self.hide()
        # check if OK button was pressed
        if self.settings_window.exec_() == QDialog.Accepted:
            self.settings_window.apply_settings()
            self.decoy_window = DecoyWindow(text='Restarting App...')
            self.decoy_window.show()
            # else statement is only for testing purposes during development
            if os.path.exists('PyAutoMate.exe'):
                os.startfile('PyAutoMate.exe')
                while True: sleep_for(500)      # wait for the other instance to close this one
            else: 
                # reaches here only if settings are opened in development environment
                sleep_for(1000)
                self.decoy_window.hide()
        self.show()
        self.restricted = False

    def add_new_button(self):
        """ creates an instance of AddButtonWindow() which is a QDialog """
        add_button_script = AddButtonWindow(self)
        add_button_script.show()
        self.restricted = True
        self.hide()

        if add_button_script.exec_() == QDialog.Accepted:
            image_path, commands_list, completion_signal = add_button_script.get_input()
            if image_path:
                with open(image_path, 'rb') as file:
                    image_bin_data = file.read()
            else:
                image_bin_data = None
            id = len(app_code)
            app_code.append([id, image_bin_data, commands_list, completion_signal])

            self.button = DraggableButton(self, id, commands_list, image_bin_data, completion_signal)
            push_button_stylesheet(self.button)
            self.place_button(self.button)
            save_app_code()
        # show the app again
        self.show()
        self.restricted = False

    def place_logo_and_title(self):
        # Properly places the logo and title
        x = ((app_size * app_grid + ((app_size // 5) * app_grid)) // 2) - (self.app_title_label.width() // 2) + (app_size // 3)
        y = self.logo_button.pos().y() + app_size // 5
        self.logo_button.setGeometry(x, y - app_size // 5, self.logo_button.width(), self.logo_button.height())
        self.app_title_label.setGeometry(x + self.logo_button.width(), y, self.font_size * 6, int(self.font_size * 1.5))

    def open_tool(self, event=None, animate: bool = True):
        if self.is_small:
            if self.app_launched:
                self.prev_xy = [self.geometry().x(), self.geometry().y()]

            window_width = (app_grid + 2) * (app_size + app_size // 10) + app_size // 10
            window_height = (app_grid) * (app_size + app_size // 10) + (2 * app_size) // 5
            target_geometry = QRect(
                screen_width // 2 - window_width // 2 - app_size,
                screen_height // 2 - window_height // 2 - app_size,
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
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(target_geometry)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def get_grid_xy(self, row=0, column=0):
        condition = row == 0 and column == 0
        padding = app_size // 10
        extra = 0 if condition else padding * 2
        return padding + column * app_size + column * padding, padding * 2 + row * app_size + row * padding + extra

    def get_row_col_by_pos(self, position) -> tuple:
        """ 
        - Takes: a position calculated using pyautogui.position()
        - Returns: a tuple of row, column where the position leads to
        """
        for i in range(app_grid):
            for j in range(app_grid+2):
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
                                        'try increasing the app grid from PyController.exe')
                    self.message_bad_grid_given = True
                widget.setGeometry(0, 0, 0, 0)
                return

        condition = row == 0 and col == 0
        extra = 0 if condition else app_size // 5
        x, y = self.get_grid_xy(row, col)
        widget.setGeometry(x, y, app_size, app_size)
        widget.setIconSize(QSize(widget.size().width() - extra, 
                                 widget.size().height() - extra))
        self.occupancies[row][col] = True

    def update_dimensions(self, from_button: bool=False) -> None:
        number_of_buttons = self.get_number_of_buttons()
        width = app_size + app_size // 5
        height = 10 + number_of_buttons * app_size + app_size // 5 + number_of_buttons * 5

        if self.prev_xy and not from_button:
            x, y = self.prev_xy
        else:
            x = screen_width - width - app_size // 5
            y = screen_height // 2 - height // 2 - app_size

        target_geometry = QRect(x, y, width, height)
        self.animate_transformation(target_geometry)

    def check_snap(self, button, initial_position):
        """
        Check if the button is near the snap spot.
        If it is, snap it to the spot.
        """
        for row in range(len(self.occupancies)):
            if self.occupancies[row][0] == False:
                width = app_size // 10
                height = width * 2 + row * app_size + row * width + width * 2
                snap_position = QPoint(width, height)

        button_position = button.pos()
        # Define a threshold for snapping
        threshold = int(app_size * 0.6)

        # Calculate the distance between the button and the snap spot
        def check_positions(self):
            for i in range(app_grid):
                if i == 0: continue
                for j in range(app_grid+2):
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

    def toggle_hide_show(self):
        """This is called from keyboard's hotkey thread."""
        if self.restricted:
            return

        print("pressed")

        # Bounce the work to Qt's main (GUI) thread
        QTimer.singleShot(0, self._toggle_visibility)

    def _toggle_visibility(self):
        """Runs in the Qt main thread."""
        if self.isHidden():
            self.show()
        else:
            self.hide()

    # def key_work(self):
    #     # if keyboard.is_pressed(app_hide_key) and not self.restricted:
    #     #     while keyboard.is_pressed(app_hide_key):
    #     #         sleep_for(50)
    #     #     if self.isHidden():
    #     #         self.show()
    #     #     else:
    #     #         self.hide()

    #     if self.assistant_text_enabled:
    #         if self.floating_textbox.is_not_visible and not self.isHidden():
    #             for key in self.allowed_keys:
    #                 if keyboard.is_pressed(key):
    #                     while keyboard.is_pressed(key): sleep_for(50)
    #                     # CAUTION: THIS IS A CHEAP TRICK TO GET THE TOOL FOCUSED ON
    #                     mouse_x, mouse_y = pyautogui.position()
    #                     # Quick move and get back logic
    #                     pyautogui.leftClick(self.x() + 15, self.y() + 15)
    #                     pyautogui.moveTo(mouse_x, mouse_y)
    #                     # Now check
    #                     self.floating_textbox.show()

    #         else:
    #             if not self.floating_textbox.text() or keyboard.is_pressed('esc'):
    #                 self.floating_textbox.hide(animation=True)
    #             elif keyboard.is_pressed('enter') and not self.isHidden():
    #                 command = self.floating_textbox.text()
    #                 self.floating_textbox.hide(animation=True)
    #                 self.floating_textbox.process_command(command)

            

    #     QTimer.singleShot(25, self.key_work)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Create rounded rectangle using QPainter
        painter.setBrush(self.background_color)
        painter.setPen(Qt.NoPen)  # Remove the border
        painter.drawRoundedRect(self.rect(), app_size // 5, app_size // 5)
        painter.end()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        text_to_add = add_spaces_for_context_menu('Hide Tool', app_hide_key)
        action1 = menu.addAction(text_to_add)
        action2 = menu.addAction('Open Tool' if self.is_small else 'Minimize Tool')
        if not self.is_small:
            menu.addSeparator()
            new_sub_menu = menu.addMenu('New')
            text_to_add = add_spaces_for_context_menu('Script', '')
            action4 = new_sub_menu.addAction(text_to_add)
            assistant_sub_menu = menu.addMenu('Assistant')
            text_to_add = add_spaces_for_context_menu(("✔️" if self.assistant_text_enabled else "❌") + " Text", '')
            action6 = assistant_sub_menu.addAction(text_to_add)
            action3 = menu.addAction("Settings")
            menu.addSeparator()
            actione = menu.addAction("Exit")
            context_menu_stylesheet(new_sub_menu)
        context_menu_stylesheet(menu)

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None: return
        elif action == action1 and not self.isHidden():
            self.hide()
        elif action == action2:
            self.open_tool()
        elif not self.is_small and action == action3:
            self.open_settings()
        elif not self.is_small and action == action4:
            self.add_new_button()
        elif not self.is_small and action == actione:
            self.floating_textbox.hide(animation=False)
            if QMessageBox.question(self, 'PyAutoMate', 'Are you sure you want to exit?') == QMessageBox.Yes:
                save_app_code()
                QApplication.quit()
        elif not self.is_small and action == action6:
            self.assistant_text_enabled = not self.assistant_text_enabled

    def hide(self):
        self.floating_textbox.hide(animation=False)
        super().hide()

    def show(self):
        super().show()

# end of MainTool class

# start of ToggleSwitch class
class ToggleSwitch(QPushButton):
    def __init__(self, parent=None, initial_state=False) -> None:
        """ 
        Initializes a QPushButton which is a toggle. Use isChecked() method to 
        check if the button is on.

        Args:
            parent (QWidget): the parent of the button.
            initial_state (bool: False): the initial state of the button.
        """
        super().__init__(parent)
        self.setCheckable(True)  # Ensures button can be toggled
        self.setFixedSize(int(app_size * 1.25), int(app_size * 0.5))
        self.setChecked(initial_state)  # Set initial state
        self.clicked.connect(self.update_style)  # Directly update style when clicked
        self.setObjectName("toggle-switch")
        self.update_style()

    def update_style(self):
        condition = self.isChecked()
        style_sheet_file = 'stylesheets/STN_toggle.css' if condition else 'stylesheets/STF_toggle.css'
        set_text_to = 'ON' if condition else 'OFF'
        # set the stylesheet and the text
        with open(style_sheet_file, 'r') as file:
            self.setStyleSheet(file.read())
        self.setText(set_text_to)
    
    def keyPressEvent(self, event):
        """ Do not perform any action on a key press """
        event.ignore()
# end of ToggleSwitch class

# start of Settings class
class Settings(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Configure App')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setFixedWidth(app_size * 7)  # Adjust as needed
        self.commands_list = []

        title_bar_widget = dialog_window_stylesheet(self)
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_widget.setLayout(main_layout)

        def label_stylesheet(widget):
            widget.setStyleSheet(" font-size: 16px; ")

        # app size setting
        self.app_size_label = QLabel('App Size', self)
        self.app_size_spinbox = QSpinBox(self)
        self.app_size_spinbox.setFixedSize(int(app_size * 1.25), int(app_size * 0.5))
        self.app_size_spinbox.setRange(30, 80)
        self.app_size_spinbox.setValue(app_size)
        # app grid setting
        self.app_grid_label = QLabel('App Grid', self)
        self.app_grid_spinbox = QSpinBox(self)
        self.app_grid_spinbox.setFixedSize(int(app_size * 1.25), int(app_size * 0.5))
        self.app_grid_spinbox.setRange(4, 12)
        self.app_grid_spinbox.setValue(app_grid)
        # app hide key setting
        self.hide_key_label = QLabel(f"Hide Key: {app_hide_key}")
        self.hide_key_selector = QPushButton('Select Key', self)
        self.hide_key_selector.setObjectName("QPushButton")
        self.hide_key_selector.clicked.connect(self.hide_key_selection)
        # dark mode setting
        self.dark_mode_label = QLabel("Dark Mode")
        self.dark_mode_toggle = ToggleSwitch(self, initial_state=app_theme == 'dark')
        self.space_label = QLabel(self)     # separator
        # OK and Cancel buttons
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setObjectName('QPushButton')
        self.ok_button = QPushButton('Apply', self)
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setObjectName('QPushButton')
        # apply styling
        label_stylesheet(self.app_grid_label)
        label_stylesheet(self.app_size_spinbox)
        label_stylesheet(self.app_size_label)
        label_stylesheet(self.app_grid_spinbox)
        label_stylesheet(self.dark_mode_label)
        label_stylesheet(self.hide_key_label)

        app_size_widget = self.create_horizontal_layout(self.app_size_label, self.app_size_spinbox)
        main_layout.addWidget(app_size_widget)
        app_grid_widget = self.create_horizontal_layout(self.app_grid_label, self.app_grid_spinbox)
        main_layout.addWidget(app_grid_widget)
        dark_mode_widget = self.create_horizontal_layout(self.dark_mode_label, self.dark_mode_toggle)
        main_layout.addWidget(dark_mode_widget)
        hide_key_widget = self.create_horizontal_layout(self.hide_key_label, self.hide_key_selector)
        main_layout.addWidget(hide_key_widget)
        main_layout.addWidget(self.space_label)
        main_layout.addWidget(self.cancel_button)
        main_layout.addWidget(self.ok_button)

        overall_layout = QVBoxLayout(self)
        overall_layout.addWidget(title_bar_widget)
        overall_layout.addWidget(main_widget)
        self.setLayout(overall_layout)
        enable_dragging(self)       # enables the dragging for this QDialog

    def apply_settings(self):
        """ sets the app_theme, app_size, app_grid """
        global app_theme, app_size, app_grid
        app_theme = 'dark' if self.dark_mode_toggle.isChecked() else 'light'
        app_size = self.app_size_spinbox.value()
        app_grid = self.app_grid_spinbox.value()
        save_app_settings()
    
    def hide_key_selection(self):
        global app_hide_key
        self.hide_key_selector.setEnabled(False)
        push_button_disabled_stylesheet(self.hide_key_selector)
        sleep_for(100)
        app_hide_key = keyboard.read_event().name
        self.hide_key_label.setText(f'Hide Key: {app_hide_key}')
        push_button_stylesheet(self.hide_key_selector)
        self.hide_key_selector.setEnabled(True)

    def create_horizontal_layout(self, widget_1, widget_2) -> QWidget:
        double_widget = QWidget(self)
        double_layout = QHBoxLayout(double_widget)
        double_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra margins
        double_layout.setSpacing(10)  # Adjust spacing between widgets
        double_widget.setLayout(double_layout)
        double_layout.addWidget(widget_1)
        double_layout.addWidget(widget_2)
        return double_widget
# end of Settings

# start of ScriptingDialog class
class ScriptingDialog(QDialog):
    def __init__(self, parent, window_title):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.main_layout = QVBoxLayout(self)
        self.labels = []
        self.buttons = []
        self.radios = []

    def add_label(self, text: str):
        self.label = QLabel(text, self)
        self.main_layout.addWidget(self.label)
# end of ScriptingDialog class

# start of ScriptOption class
class ScriptOption(QDialog):
    def __init__(self, ok_button_name: str, functions: dict[str, Callable]=None, 
                 radios: list[str]=None, inputs: list[str]=None):
        super().__init__()
        self.setWindowTitle('Select An Option')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setFixedWidth(app_size * 7)
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
        super().__init__(parent)
        self.highlighter = KeywordHighlighter(self.document())
        self.setFixedHeight(app_size * 7)

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
        context_menu_stylesheet(menu)

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
    def __init__(self, parent, commands_list: list[list]=None, existing_image: str=None, completion_signal=False):
        super().__init__(parent)
        self.setWindowTitle("Script Editor")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setFixedWidth(int(screen_width * 0.75))
        self.parent = parent
        self.commands_list = []
        title_bar_widget = dialog_window_stylesheet(self)

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

        self.input_field = CustomTextEdit(self)
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
        self.move(screen_width // 2 - self.width() // 2, screen_height // 2 - self.height() // 2)
        
    def set_icon_or_not(self):
        if self.includes_icon.isChecked():
            self.select_icon_button.setEnabled(True)
            push_button_stylesheet(self.select_icon_button)
            self.icon_label.setText(f'Icon: Selected' if self.file_path else 'Icon: Not Selected')
        else:
            self.select_icon_button.setEnabled(False)
            push_button_disabled_stylesheet(self.select_icon_button)
            self.icon_label.setText('Icon: Disabled')

    def action_recorder(self):
        """ the best of all script writer buttons, records clicks, double clicks automatically, with time intervals too """
        # self.button_references[0].setEnabled(False)
        option_window = ScriptOption("Start Recording", radios=['Add Time Intervals', 'Ignore Time Intervals'])

        if option_window.exec_() == QDialog.Accepted:
            QMessageBox.information(self, 'PyAutoMate', 'Usage:\n  l -> left click\n'
                                    '  r -> right click\n  d -> double click')
            include_time = True if option_window.get_selected_option().startswith('Add') else False
            current_position = self.pos()
            self.move(screen_width, 0)
            main_loop_flag = True

            def write_script_for_action(start_time, stop_key: str, click_type: str, func_to_run: Callable):
                if include_time:
                    self.input_field.insertPlainText(f'wait time {round(time.time() - start_time, 0) + 0.6}\n')
                while keyboard.is_pressed(stop_key): sleep_for(25)
                location = pyautogui.position()
                self.input_field.insertPlainText(f'click {click_type} cor {location.x} {location.y}\n')
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
            option_window.move(screen_width, 0)
            if button_type == 'double':
                button_to_wait = 'left'
            else: button_to_wait = button_type
            while not mouse.is_pressed(button_to_wait): sleep_for(25)
            while mouse.is_pressed(button_to_wait): sleep_for(25)
            position = pyautogui.position()
            # calls the dialog back to the last saved position
            option_window.move(current_position.x(), current_position.y())
            if option_window.get_selected_option().endswith('Coordinates'):
                self.input_field.insertPlainText(f'click {button_type} cor {position.x} {position.y}\n')
            elif option_window.get_selected_option().endswith('Image'):
                id = save_screenshot(position)
                self.input_field.insertPlainText(f'click {button_type} img 10.0 {id}\n')

        def save_screenshot(position: tuple) -> int:
            """ saves the 16x16 screenshot of the given location, and returns the save path """
            shot = pyautogui.screenshot(region=(position.x - 8, position.y - 8, 16, 16))
            loopFlag = True
            while loopFlag:
                loopFlag = False
                id = random.randint(1000000, 9999999)
                for script in app_code:
                    if script[0] == id:
                        loopFlag = True
            buffer = BytesIO()
            shot.save(buffer, format="PNG")  # Save as PNG (or another format)
            app_code.append([id, buffer.getvalue(), None, False])
            save_app_code()
            return id

        self.move(screen_width, 0)
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
                self.input_field.insertPlainText(f'open loc {file_path}')
        def open_folder():
            folder_path = QFileDialog.getExistingDirectory(parent=self, caption="Select Folder", 
                                                           options=QFileDialog.Options())
            if folder_path:
                self.input_field.insertPlainText(f'open loc {folder_path}')
        def open_link():
            text, ok = QInputDialog.getText(self, "Open Website Link", "Paste Website Link Here:", flags=Qt.Tool)
            if ok and text:  # If user clicks OK and input is not empty
                self.input_field.insertPlainText(f'open link {text}\n')

        context_menu = QMenu(self)
        context_menu_stylesheet(context_menu)
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
            approval = self.debugger()
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

    def debugger(self) -> None:
        """ debugs and compiles the script """
        mouse_buttons = ['left', 'right', 'middle']
        keyboard_buttons = [
            'left ctrl', 'alt gr', 'ctrl', 'left shift', 'left alt', 'right ctrl', 'windows', 
            'right alt', 'alt', 'shift', 'right windows', 'right shift', 'left windows',
            'backspace', 'caps lock', 'delete', 'down', 'end', 'enter', 'esc', 'escape',  
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',  
            'home', 'insert', 'left', 'num lock', 'page down', 'page up', 'pause', 'print screen',  
            'right', 'scroll lock', 'shift', 'space', 'tab', 'up',  
            'alt', 'alt gr', 'ctrl', 'menu', 'super',  
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',  
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',  
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',  
            '`', '-', '=', '[', ']', '\\', ';', "'", ',', '.', '/'
        ]
        try:
            for command in self.commands_list:
                index = self.commands_list.index(command)
                all_categories = ['click', 'open', 'wait', 'keyboard', 'show']
                if not command: pass
                elif command[0] in all_categories:
                    self.commands_list[index][0] = all_categories.index(command[0]) + 1
                    click_categories = ['left', 'right', 'double']
                    click_sub_categories = ['cor', 'img']
                    open_categories = ['loc', 'link']
                    wait_categories = ['time', 'img', 'key']
                    wait_sub_key_categories = ['keyboard', 'mouse']
                    keyboard_categories = ['type', 'press']
                    # no need for a category for show window
                    # for clicks
                    if self.commands_list[index][0] == 1 and self.commands_list[index][1] in click_categories:
                        self.commands_list[index][1] = click_categories.index(command[1]) + 1
                        self.commands_list[index][2] = click_sub_categories.index(command[2]) + 1
                        # for coordinates clicks
                        if self.commands_list[index][2] == 1:
                            self.commands_list[index][3] = int(self.commands_list[index][3])
                            self.commands_list[index][4] = int(self.commands_list[index][4])
                        # for image clicks
                        elif self.commands_list[index][2] == 2:
                            self.commands_list[index][3] = float(self.commands_list[index][3])
                            self.commands_list[index][4] = int(self.commands_list[index][4])
                        else: return False
                    # for opening
                    elif self.commands_list[index][0] == 2 and self.commands_list[index][1] in open_categories:
                        self.commands_list[index][1] = open_categories.index(command[1]) + 1
                        # for local files
                        if self.commands_list[index][1] == 1:
                            try:
                                self.commands_list[index][2] = ' '.join(self.commands_list[index][2:])
                                del self.commands_list[index][3:]
                            except: pass
                        # for websites on default browser
                        elif self.commands_list[index][1] == 2:
                            pass
                        else: return False
                    # for waiting
                    elif self.commands_list[index][0] == 3 and self.commands_list[index][1] in wait_categories:
                        self.commands_list[index][1] = wait_categories.index(command[1]) + 1
                        # for a specified time
                        if self.commands_list[index][1] == 1:
                            self.commands_list[index][2] = float(self.commands_list[index][2])
                        # for a specific image
                        elif self.commands_list[index][1] == 2:
                            self.commands_list[index][2] = float(self.commands_list[index][2])
                            self.commands_list[index][3] = int(self.commands_list[index][3])
                        # for specific button presses
                        elif self.commands_list[index][1] == 3 and self.commands_list[index][2] in wait_sub_key_categories:
                            self.commands_list[index][2] = wait_sub_key_categories.index(command[2]) + 1
                            # for keyboard button presses
                            if (self.commands_list[index][2] == 1 and 
                                self.commands_list[index][3] in keyboard_buttons): pass
                            # for mouse button presses
                            elif (self.commands_list[index][2] == 2 and 
                                  self.commands_list[index][3] in mouse_buttons): pass
                            else: return False
                        else: return False
                    # for doing some keyboard type action
                    elif self.commands_list[index][0] == 4 and self.commands_list[index][1] in keyboard_categories:
                        self.commands_list[index][1] = keyboard_categories.index(command[1]) + 1
                        # for typing
                        if self.commands_list[index][1] == 1:
                            total_indices = len(command)
                            try:
                                self.commands_list[index][2] = ' '.join(self.commands_list[index][2:total_indices])
                                for i in range(total_indices):
                                    if i > 2:
                                        del self.commands_list[index][i]
                            except Exception as e: print(e)
                        # for pressing hotkeys
                        elif self.commands_list[index][1] == 2:
                            total_indices = len(command)
                            temp = ' '.join(self.commands_list[index][2:total_indices])
                            self.commands_list[index] = [4, 2, temp]
                        else: return False
                    # for showing a specific window
                    elif self.commands_list[index][0] == 5:
                        total_indices = len(command)
                        try:
                            self.commands_list[index][1] = ' '.join(self.commands_list[index][1:total_indices])
                            for i in range(total_indices):
                                if i > 1:
                                    del self.commands_list[index][i]
                        except Exception as e: print(e)
                    else: return False
                else: return False
        except Exception as e:
            return False
        return True # if no errors occur

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
    def __init__(self, parent, id: int, code_to_run, icon_to_set, completion_signal):
        super().__init__(parent)
        self.dragging = False
        self.position = (0, 0)
        self.code_to_run = code_to_run
        self.icon_to_set = icon_to_set
        self.id = id
        self.completion_signal = completion_signal
        self.window = parent
        self.setObjectName("QPushButton")
        if icon_to_set is not None:
            self.define_icon(self.icon_to_set)

    def define_icon(self, icon_bin_data):
        self.setIcon(binary_to_qicon(icon_bin_data))

    def reverse_compiler(self) -> None:
        """ debugs and compiles the script """
        commands_list = self.code_to_run
        for command in commands_list:
            if not command: continue
            else: index = commands_list.index(command)
            if command[0] == 1:
                commands_list[index][0] = 'click'
                if command[1] == 1:
                    commands_list[index][1] = 'left'
                elif command[1] == 2:
                    commands_list[index][1] = 'right'
                elif command[1] == 3:
                    commands_list[index][1] = 'double'
                if command[2] == 1:
                    commands_list[index][2] = 'cor'
                elif command[2] == 2:
                    commands_list[index][2] = 'img'
            elif command[0] == 2:
                commands_list[index][0] = 'open'
                if command[1] == 1:
                    commands_list[index][1] = 'loc'
                elif command[1] == 2:
                    commands_list[index][1] = 'link'
            elif command[0] == 3:
                commands_list[index][0] = 'wait'
                if command[1] == 1:
                    commands_list[index][1] = 'time'
                elif command[1] == 2:
                    commands_list[index][1] = 'img'
                elif command[1] == 3:
                    commands_list[index][1] = 'key'
                    if command[2] == 1:
                        commands_list[index][2] = 'keyboard'
                    elif command[2] == 2:
                        commands_list[index][2] = 'mouse'
            elif command[0] == 4:
                commands_list[index][0] = 'keyboard'
                if command[1] == 1:
                    commands_list[index][1] = 'type'
                elif command[1] == 2:
                    commands_list[index][1] = 'press'
            elif command[0] == 5:
                commands_list[index][0] = 'show'

        add_button_window = AddButtonWindow(parent=main_tool, commands_list=commands_list, 
                                      completion_signal=self.completion_signal,
                            existing_image=self.icon_to_set)
        main_tool.restricted = True
        main_tool.hide()

        if add_button_window.exec_() == QDialog.Accepted:
            # If OK was pressed, display the input from the second window
            image_path, commands_list, completion_signal = add_button_window.get_input()
            image_bin_data = None
            self.completion_signal = completion_signal
            self.code_to_run = commands_list
            if image_path and image_path != self.icon_to_set:
                with open(image_path, 'rb') as file:
                    image_bin_data = file.read()
                self.icon_to_set = image_bin_data
                self.define_icon(image_bin_data)
            for script in app_code:
                index = app_code.index(script)
                if script[0] == self.id:
                    if image_path != self.icon_to_set: app_code[index][1] = image_bin_data
                    app_code[index][2] = commands_list
                    app_code[index][3] = completion_signal
            save_app_code()
        main_tool.show()
        main_tool.restricted = False

    def delete_button_event(self):
        if not self.parent().is_small:
            if QMessageBox.question(self, 'PyAutoMate', 'Are you sure you want to delete this button?') == QMessageBox.Yes:
                for script in app_code:
                    if script[0] == self.id:
                        app_code.remove(script)
                i, j = self.parent().get_row_col_by_pos(self.position)
                self.parent().occupancies[i][j] = False
                self.hide()
            else:
                self.parent().check_snap(self, self.position)

    def run_button_script(self):
        executer(self, commands=self.code_to_run, comp_signal=self.completion_signal)

    def mouseDoubleClickEvent(self, event):
        self.run_button_script()
    def mousePressEvent(self, event):
        if self.parent().is_small and event.button() == Qt.LeftButton:
            while mouse.is_pressed('left'): sleep_for(25)
            self.run_button_script()
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
        if not self.parent().is_small:
            menu = QMenu(self)
            text_to_add = add_spaces_for_context_menu("Run Script", '')
            action4 = menu.addAction(text_to_add)
            menu.addSeparator()
            text_to_add = add_spaces_for_context_menu("Edit Script", '')
            action2 = menu.addAction(text_to_add)
            action3 = menu.addAction("Add Icon" if self.icon_to_set is None else 'Edit Icon')
            action5 = None
            if self.icon_to_set is not None:
                text_to_add = add_spaces_for_context_menu("Remove Icon", '')
                action5 = menu.addAction(text_to_add)
            menu.addSeparator()
            action1 = menu.addAction("Delete")
            context_menu_stylesheet(menu)

            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == action1:
                self.delete_button_event()
                save_app_code()
            elif action == action2:
                self.reverse_compiler()
                save_app_code()
            elif action == action3:
                image_path, _ = QFileDialog.getOpenFileName(
                                    parent=self,
                                    caption="Select An Image",
                                    filter="Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff *.svg);;All Files (*)",
                                    options=QFileDialog.Options())
                if image_path:
                    with open(image_path, 'rb') as file:
                        image_bin_data = file.read()
                    self.icon_to_set = image_bin_data
                    self.define_icon(image_bin_data)
                    for script in app_code:
                        index = app_code.index(script)
                        if script[0] == self.id:
                            app_code[index][1] = image_bin_data
                    save_app_code()
            elif action == action4:
                self.run_button_script()
            elif action5 and action == action5:
                self.setIcon(QIcon())
                self.icon_to_set = None
                for script in app_code:
                    index = app_code.index(script)
                    if script[0] == self.id:
                        app_code[index][1] = None
                save_app_code()
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

def context_menu_stylesheet(widget):
    widget.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
    widget.setAttribute(Qt.WA_TranslucentBackground)
    font = QFont("Arial", 10)
    widget.setFont(font)
    
    style_sheet_file = 'stylesheets/STL_context_menu.css' if app_theme == 'light' else 'stylesheets/STD_context_menu.css'
    with open(style_sheet_file, 'r') as file:
        widget.setStyleSheet(file.read())

def dialog_window_stylesheet(dialog_window):
    # Create title and close button
    title_label = QLabel(dialog_window.windowTitle())
    title_label.setObjectName("title-label")
    close_button = QPushButton("X")
    close_button_size = int(app_size / 1.75)
    close_button.setFixedSize(close_button_size, close_button_size)
    close_button.setObjectName("close-button")
    close_button.clicked.connect(dialog_window.reject)

    # Layout for title bar
    Hlayout = QHBoxLayout()
    Hlayout.addWidget(title_label)
    Hlayout.addWidget(close_button, alignment=Qt.AlignRight)
    title_bar_widget = QWidget(dialog_window)
    title_bar_widget.setLayout(Hlayout)

    style_sheet_file = 'stylesheets/STL_dialog.css' if app_theme == 'light' else 'stylesheets/STD_dialog.css'
    with open(style_sheet_file, 'r') as file:
        dialog_window.setStyleSheet(file.read())
    return title_bar_widget

def push_button_stylesheet(button):
    style_sheet_file = 'stylesheets/STL_button.css' if app_theme == 'light' else 'stylesheets/STD_button.css'
    with open(style_sheet_file, 'r') as file:
        button.setStyleSheet(file.read())

def push_button_disabled_stylesheet(button):
    style_sheet_file = 'stylesheets/STL_button_disabled.css' if app_theme == 'light' else 'stylesheets/STD_button_disabled.css'
    with open(style_sheet_file, 'r') as file:
        button.setStyleSheet(file.read())

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
            x = max(0, min(widget.x(), screen_width - widget.width()))
            y = max(0, min(widget.y(), screen_height - widget.height()))
            widget.move(x, y)
            event.accept()

    widget.mousePressEvent = mousePressEvent
    widget.mouseMoveEvent = mouseMoveEvent
    widget.mouseReleaseEvent = mouseReleaseEvent

""" executer function """
def executer(parent: QWidget, commands: list[list], comp_signal: bool=False) -> None:
    """
    takes in a list of executer readable commands with the proper format to execute them.
    Command[0]: the type of the command
    Command[1]: the specification of the type

    param: parent is a widget on which the dialogs would be set
    param: commands is a list of lists, where each list represents a command
    param: variables (dict)
    param: comp_signal if true, provides a signal on completion of the script, false by default
    param: dialogs_parent (ptr) points to the window hosting the dialogs, i.e. small tool

    """
    main_tool.restricted = True
    main_tool.hide()
    sleep_for(100)
    for command in commands:
        # if command is empty or just a \n
        if not command: pass
        # for mouse clicks
        elif command[0] == 1:
            # the click type, left, right, or double
            if command[1] == 1: click_function = pyautogui.leftClick
            elif command[1] == 2: click_function = pyautogui.rightClick
            elif command[1] == 3: click_function = pyautogui.doubleClick
            # click by coordinates
            if command[2] == 1:
                x = command[3]
                y = command[4]
                click_function(x, y)
            # click by image, also requires timeout
            elif command[2] == 2:
                timeout = command[3]
                image_id = int(command[4])
                for script in app_code:
                    if script[0] == image_id:
                        image_data = script[1]
                x, y = find_image_location(image_data, timeout)
                if x and y:
                    click_function(x, y)
                else:
                    QMessageBox.critical(parent, 'PyAutoMate', f'The required image was not Found within {timeout} seconds')
                    break
        # for opening
        elif command[0] == 2:
            # for local files
            if command[1] == 1:
                file_path = command[2]
                if os.path.exists(file_path):
                    os.startfile(file_path)
                else:
                    QMessageBox.critical(parent, 'PyAutoMate', f'{file_path} does not exist')
            # for websites on default browser
            elif command[1] == 2:
                link = command[2]
                webbrowser.open(link)
        # for waiting
        elif command[0] == 3:
            # for waiting for a specified time
            if command[1] == 1:
                sleep_time = int(command[2] * 1000)
                sleep_for(sleep_time)
            # for waiting for a specific image to appear
            elif command[1] == 2:
                timeout = command[2]
                image_id = int(command[3])
                for script in app_code:
                    if script[0] == image_id and not find_image_location(script[1], timeout):
                        QMessageBox.critical(parent, 'PyAutoMate', f'The required image was not Found within {timeout} seconds')
                        break
            # for waiting for a button press
            elif command[1] == 3:
                button = command[3]
                # for keyboard press
                if command[2] == 1:
                    while not keyboard.is_pressed(button): sleep_for(25)
                    while keyboard.is_pressed(button): sleep_for(25)
                # for mouse press
                elif command[2] == 2:
                    while not mouse.is_pressed(button): sleep_for(25)
                    while mouse.is_pressed(button): sleep_for(25)
        # for doing some keyboard type action
        elif command[0] == 4:
            # for typing
            if command[1] == 1:
                content = command[2]
                pyautogui.typewrite(content, interval=0.005)
            # for pressing hotkeys
            elif command[1] == 2:
                button = command[2].split()   # assuming command[2] is a list
                pyautogui.hotkey(button)
                sleep_for(500)
        # for activating a window
        elif command[0] == 5:
            window_title = command[1]
            show_window(window_title)
    # optionally provide a completion signal
    if comp_signal:
        QMessageBox.information(parent, 'PyAutoMate', f'Script was executed successfully')
    main_tool.show()
    main_tool.restricted = False

""" executer helper functions """

def find_image_location(binary_data: str, timeout: float) -> tuple:
    """
    helper function for executer to find images on the screen, 
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

def show_window(window_title: str, timeout: int=0) -> None:
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
            QMessageBox.critical(main_tool, 'PyAutoMate', f'Window with title {window_title} was not found')
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
                QMessageBox.critical(main_tool, 'PyAutoMate', 'An unexpected error occured. '
                        'Please contact the developer if the issue persists.')
                sys.exit(1)

def binary_to_qicon(binary_img) -> QIcon:
    pixmap = QPixmap()
    # if statement required for this function
    if not pixmap.loadFromData(binary_img):
        raise ValueError(f'failed to load image data for an image')
    return QIcon(pixmap)

def save_app_code():
    with open('script.bin', 'wb') as file:
        pickle.dump(app_code, file)

def save_app_settings():
    with open('settings.bin', 'wb') as file:
        app_settings = {
            'hide key': app_hide_key,
            'theme': app_theme,
            'app size': app_size,
            'app grid': app_grid
        }
        pickle.dump(app_settings, file)

def load_app_data() -> tuple:
    with open('script.bin', 'rb') as file:
        app_code = pickle.load(file)
    with open('settings.bin', 'rb') as file:
        app_settings = pickle.load(file)
    return app_code, app_settings

""" Program Starts From Here After Imports """
if __name__ == "__main__":
    # check for all the required files and stylesheets
    required_files = ['settings.bin', 'script.bin']
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
        
    # load app settings and app code to global memory
    app_code, app_settings = load_app_data()
    app_hide_key = app_settings['hide key']
    app_size = int(app_settings['app size'])
    app_grid = int(app_settings['app grid'])
    app_theme = app_settings['theme']

    # get screen width and height
    screen_width = pyautogui.size()[0]
    screen_height = pyautogui.size()[1]
    app_logo = None
    for script in app_code: 
        if script[0] == 0: 
            app_logo = script[1]

    # create the app root
    close_other_instances()
    root_app.setWindowIcon(binary_to_qicon(app_logo))
    main_tool = MainTool()
    # Activate the Assistant
    # QTimer.singleShot(0, main_tool.activate_assistant)
    main_tool.show() # finally, show the main tool
    loading_window.hide()
    # main_tool.key_work()    # activates the shortcut key of app hide

    # UPDATE: key work using keyboard module
    # keyboard.add_hotkey(app_hide_key, main_tool.toggle_hide_show)
    root_app.exec_()   # should never exit from here
    sys.exit(1)