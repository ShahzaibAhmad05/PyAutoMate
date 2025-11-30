# PyQt5 imports
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QDialog, QMessageBox, QMenu
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QColor, QPainter

# python libraries
import os, sys, shutil, pyautogui

# self-defined modules
from modules.getters import get_settings, get_logo_path
from modules.utils import save_script, enableDragging, generateRandomID, add_spaces_for_context_menu
from modules.sysUtils import sleep_for
from Assistant import GlobalTextBox

# UI elements
from ui.settings import Settings
from ui.scriptEditorWindow import ScriptEditorWindow
from ui.draggableButton import DraggableButton

# CSS Styling functions
from modules.styling import (push_button_stylesheet, context_menu_stylesheet)

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
        enableDragging(self)
        self.initUI()

        # Assistant control variables
        self.assistant_text_enabled = True
        self.floating_textbox = GlobalTextBox(self)


    def initUI(self) -> None:
        """ Initialize the UI components of the main window """
        # setup logo button
        self.logo_button = QPushButton(self)
        self.logo_button.setIcon(QIcon(get_logo_path()))
        self.logo_button.setStyleSheet("QPushButton { border: none; }")
        self.logo_button.mouseDoubleClickEvent = self.open_tool
        
        # to enable dragging using the logo
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
        # Activate sub-windows
        self.settingsWindow = Settings(self)
        
    def openSettings(self) -> None:
        """ creates an instance of Settings() which is a QDialog """
        self.settingsWindow.show()
        self.hide()
        
        # check if OK button was pressed
        if self.settingsWindow.exec_() == QDialog.Accepted:
            self.settingsWindow.save_settings()
            # else statement is only for testing purposes during development
            if os.path.exists('PyAutoMate.exe'):
                os.startfile('PyAutoMate.exe')
                while True: sleep_for(500)      # wait for the other instance to close this one
            else: 
                # reaches here only if settings are opened in development environment
                sleep_for(1000)
                self.decoy_window.hide()
        self.show()

    def addNewButton(self):
        """ creates an instance of ScriptEditorWindow() which is a QDialog """
        scriptEditor = ScriptEditorWindow(self, code=None,
                                            existing_image=None, completionSignal=False)
        scriptEditor.show()
        self.hide()     # hide main tool only after editor is shown

        if scriptEditor.exec_() == QDialog.Accepted:
            image_path, code, completionSignal = scriptEditor.get_input()
            scriptID = generateRandomID()
            iconID = None

            # save the icon if given
            if os.path.exists(image_path):
                iconID = generateRandomID()
                shutil.copy(image_path, iconID)

            save_script(scriptID, iconID, code, completionSignal)
            # show the button for this instance too
            self.button = DraggableButton(self, scriptID)
            push_button_stylesheet(self.button, self)
            self.place_button(self.button)

        self.show()

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
            self.addNewButton()

        elif not self.is_small and action == actione:
            self.floating_textbox.hide(animation=False)
            if QMessageBox.question(self, 'PyAutoMate', 
                                    'Are you sure you want to exit?') == QMessageBox.Yes:
                QApplication.quit()

        elif not self.is_small and action == action6:
            self.assistant_text_enabled = not self.assistant_text_enabled

    def show(self):     # Safety lock so nothing bad happens while tool is hidden
        super().show()
        self.restricted = False

    def hide(self):
        self.restricted = True
        super().hide()

    """ App geometry functions that are not to be touched for now """

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
