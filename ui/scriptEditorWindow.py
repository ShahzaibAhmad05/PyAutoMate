# PyQt5 imports
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QPushButton, QMessageBox, QVBoxLayout, QTextEdit, QFileDialog, QMenu, QInputDialog, QCheckBox, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

# python libraries
import os, time, pyautogui, keyboard, mouse
from typing import Callable
from pygetwindow import getActiveWindow

# self-defined modules
from modules.sysUtils import sleep_for
from modules.styling import dialog_window_stylesheet, context_menu_stylesheet, push_button_stylesheet, push_button_disabled_stylesheet
from modules.utils import enableDragging, add_spaces_for_context_menu, generateRandomID
from modules.getters import get_icon_path
from modules.debugger import debug

# UI elements
from ui.scriptingTextEdit import ScriptingTextEdit
from ui.scriptOption import ScriptOption


class ScriptEditorWindow(QDialog):
    def __init__(self, mainTool, code: list[list], existing_image: str, 
                 currentKey: str, completionSignal):
        super().__init__(mainTool)

        self.mainTool = mainTool
        self.setWindowTitle("Script Editor")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setFixedWidth(int(pyautogui.size()[0] * 0.75))
        self.code = []
        self.key = currentKey        # shortcut key for the button
        title_bar_widget = dialog_window_stylesheet(self, self.mainTool)

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

        self.input_field = ScriptingTextEdit(self.mainTool)
        font = self.input_field.font()
        font.setPointSize(14)
        self.input_field.setFont(font)
        self.input_field.setProperty("customFontSize", 14)  # Store initial font size
        self.input_field.wheelEvent = lambda event: wheel_event_for_textbox(self.input_field, event)

        if code:
            for command in code:
                for word in command:
                    index = command.index(word)
                    if type(word) != str:
                        command[index] = str(command[index])
                command = ' '.join(command)
                self.input_field.append(command)
        main_layout.addWidget(self.input_field)

        # adding shortcut key for the button
        self.selectKeyButton = QPushButton("Select Key", self)
        self.selectKeyButton.clicked.connect(self.selectKey)
        main_layout.addWidget(self.selectKeyButton)
        self.selectKeyButton.setObjectName("QPushButton")
        # label to show the selected key
        self.selectKeyLabel = QLabel('', self)
        main_layout.addWidget(self.selectKeyLabel)

        # adding icon for the button
        self.select_icon_button = QPushButton("Select Icon", self)
        self.select_icon_button.clicked.connect(self.select_icon)
        main_layout.addWidget(self.select_icon_button)
        self.select_icon_button.setObjectName("QPushButton")
            
        # label to show the selected icon's path
        if existing_image is None:
            self.file_path = ''
            self.icon_label = QLabel("Not Selected", self)
        else:
            self.file_path = existing_image
            self.icon_label = QLabel(f"Selected")
        main_layout.addWidget(self.icon_label)
        self.button.setObjectName("QPushButton")

        # checkbox to indicate if the button has a key or not
        self.selectKeyCheckbox = QCheckBox('Include Key', self)
        self.selectKeyCheckbox.setStyleSheet(" margin-top: 15px;")
        self.selectKeyCheckbox.setChecked(True if self.key else False)
        main_layout.addWidget(self.selectKeyCheckbox)

        # checkbox to decide whether to include icon or not
        self.includes_icon = QCheckBox('Include Icon', self)
        self.includes_icon.setChecked(True if self.file_path else False)
        
        # call to connect the four attr: btn, label, checkbox, key
        self.setButtonLabelGrp(self.selectKeyCheckbox, self.selectKeyButton,
                               self.selectKeyLabel, self.key)
        self.selectKeyCheckbox.toggled.connect(
            lambda _, checkbox=self.selectKeyCheckbox, attAttr=self.key, 
            attButton=self.selectKeyButton, attLabel=self.selectKeyLabel: 
            self.setButtonLabelGrp(checkbox, attButton, attLabel, attAttr)
        )

        # call once to connect the four
        self.setButtonLabelGrp(self.includes_icon, self.select_icon_button,
                               self.icon_label, self.file_path)
        self.includes_icon.toggled.connect(
            lambda checked, checkbox=self.includes_icon, attAttr=self.file_path, 
            attButton=self.select_icon_button, attLabel=self.icon_label: 
            self.setButtonLabelGrp(checkbox, attButton, attLabel, attAttr)
        )

        main_layout.addWidget(self.includes_icon)
        self.completion_check = QCheckBox('Include Completion Signal', self)
        self.completion_check.setChecked(completionSignal)
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
        enableDragging(self)

        # center the window on the screen
        self.adjustSize()
        self.move(pyautogui.size()[0] // 2 - self.width() // 2, pyautogui.size()[1] // 2 - self.height() // 2)

    def selectKey(self):
        """ Waits till a key is selected for the button """
        push_button_disabled_stylesheet(self.selectKeyButton, self.mainTool)
        self.key = keyboard.read_hotkey(suppress=False)      # prevent Windows intervention
        self.selectKeyLabel.setText(f"Selected: {self.key}")
        push_button_stylesheet(self.selectKeyButton, self.mainTool)
        
    def setButtonLabelGrp(self, checkbox: QCheckBox, attButton: QPushButton, 
                        attLabel: QLabel, attAttr) -> None:
        """ 
        Generic function attached to checkboxes and labels to enable, disable buttons, 
        and change text.
            
        Args:
            checkbox: a reference to the checkbox which is being toggled.
            attButton: reference to the attached button to enable/disable.
            attLabel: reference to the attached label to change.
            attAttr: reference to the attribute to check for the label's value
        """

        if checkbox.isChecked():
            attButton.setEnabled(True)
            push_button_stylesheet(attButton, self.mainTool)
            attLabel.setText(f'Selected: {attAttr}' if attAttr else 'Not Selected')
        else:
            attButton.setEnabled(False)
            push_button_disabled_stylesheet(attButton, self.mainTool)
            attLabel.setText('Disabled')

    def action_recorder(self):
        """ the best of all script writer buttons, records clicks, double clicks automatically, with time intervals too """
        # self.button_references[0].setEnabled(False)
        option_window = ScriptOption(self.mainTool, "Start Recording", radios=['Add Time Intervals', 'Ignore Time Intervals'])

        if option_window.exec_() == QDialog.Accepted:
            QMessageBox.information(self, 'PyAutoMate', 'Usage:\n  l -> left click\n'
                                    '  r -> right click\n  d -> double click\n Ctrl+C to finish')
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
        option_window = ScriptOption(self.mainTool, "Back", functions, ['Click by Coordinates', 'Click by Image'])
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
        context_menu_stylesheet(context_menu, self.mainTool)
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

        option_window = ScriptOption(self.mainTool, "OK", radios=['Keyboard', 'Mouse', 'Seconds'], 
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
        option_window = ScriptOption(self.mainTool, "OK", radios=['Type this (text)', 'Press these (shortcut keys)'], inputs=['Text or Buttons'])

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

        option_window = ScriptOption(self.mainTool, "OK", inputs=['Window Title: '], 
                                     functions={'Capture Next Window\'s Title': capture_window_title})
        if option_window.exec_() and option_window.get_input_values()[0].text():
            self.input_field.insertPlainText(f'show {option_window.get_input_values()[0].text()}')
        self.input_field.setFocus()

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

    def on_ok(self) -> None:
        if not self.input_field.toPlainText():
            QMessageBox.critical(self, 'PyAutoMate', 'The compilation cannot be done because the script is empty.')
        else:
            script = self.input_field.toPlainText().splitlines()
            self.code = []                    # empty the stored code
            for line in script:
                line = line.split(' ')        # make it a list of words
                self.code.append(line)        # add each list to the code

            approval = debug(self.code)
            if approval:
                if not self.file_path and self.includes_icon.isChecked() and QMessageBox.critical(self, 'PyAutoMate', 
                    'The compilation cannot be done because no icon was chosen for the button. '
                    'Uncheck \'Include Icon\' to get rid of this error.'):
                    self.code = []
                else:
                    self.accept()
            else:
                QMessageBox.critical(self, 'PyAutoMate', 
                                     'Incorrect syntax, the script could not be compiled.')
                self.code = []

    """ helpers for the on_ok function """
    
    def getIconID(self):
        """ Returns the iconID """
        if not self.includes_icon.isChecked(): return None
        return self.file_path
    
    def getCode(self):
        return self.code
    
    def getCompletionSignal(self):
        return self.completion_check.isChecked()
    
    def getKey(self):
        if not self.selectKeyCheckbox.isChecked(): return None
        return self.key
