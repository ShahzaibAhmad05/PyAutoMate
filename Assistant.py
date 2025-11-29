from PyQt5.QtWidgets import QLineEdit, QApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
import subprocess, webbrowser, sys, os
import keyboard
import threading
import time
import string
import pyautogui
from PyQt5.QtCore import QPropertyAnimation, QRect
from PyQt5.QtCore import QEasingCurve
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap
import json

def sleep_for(sleep_time: int) -> None:
    """ 
    Calls a sleep event without blocking the app's loop.
    Args:
        sleep_time (int): requires time given in ms.
    """
    loop = QEventLoop()
    QTimer.singleShot(sleep_time, loop.quit)    # assuming sleep_time is in ms
    loop.exec_()

class GlobalTextBox(QLineEdit):
    def __init__(self, main_tool):
        super().__init__()
        super().hide()
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create the animation
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)  # 1 = QEasingCurve.InOutQuad
        # Set Initial Geometry
        self.textbox_height = 40

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        if main_tool.app_theme == 'dark':
            self.setStyleSheet("""
                QLineEdit { 
                    padding: 6px; 
                    font-size: 18px;
                    border-radius: 12px;
                    font-family: "Open Sans", Arial, sans-serif;
                    background-color: rgb(35, 35, 35);
                    border: 2px solid rgb(0, 131, 172);
                    color: rgb(255, 255, 255); 
                }
            """)
        else:
            self.setStyleSheet("""
                QLineEdit { 
                    padding: 6px; 
                    font-size: 18px;
                    border-radius: 12px;
                    font-family: "Open Sans", Arial, sans-serif;
                    background-color: rgb(255, 255, 255);
                    border: 2px solid rgb(0, 131, 172);
                    color: rgb(0, 0, 0); 
                }
            """)
        
        # style_sheet_file = 'stylesheets/STL_dialog.css' if main_tool.app_theme == 'light' else 'stylesheets/STD_dialog.css'
        # with open(style_sheet_file, 'r') as file:
        #     self.setStyleSheet(file.read())
        # Start keyboard hook
        self.hook_running = False
        self.start_keyboard_hook()

        self.main_tool = main_tool
        # Set visibility, starting Geometry
        self.is_not_visible = True
        self.setGeometry(main_tool.x(), main_tool.y(), main_tool.width(), self.textbox_height)
        self.distance_from_tool = 10 + self.textbox_height
        # Keep updating geometry based on main tool position
        self.check_if_tool_moved()
        
    def start_keyboard_hook(self):
        if not self.hook_running:
            self.hook_running = True
            hook_thread = threading.Thread(target=self._keyboard_hook_thread)
            hook_thread.daemon = True
            hook_thread.start()

    def _keyboard_hook_thread(self):
        def callback(event):
            if event.event_type == keyboard.KEY_DOWN:
                # Ignore modifier keys
                if event.name in ['ctrl', 'alt', 'shift', 'windows', 'cmd']:
                    return
                
                # Get the actual character
                char = event.name
                if len(char) == 1:  # Single character
                    current_text = self.text()
                    cursor_pos = self.cursorPosition()
                    
                    # Insert character at cursor position
                    new_text = current_text[:cursor_pos] + char + current_text[cursor_pos:]
                    self.setText(new_text)
                    self.setCursorPosition(cursor_pos + 1)
                
                # Handle special keys
                elif event.name == 'space':
                    self.insert(' ')
                elif event.name == 'backspace':
                    self.backspace()
                elif event.name == 'enter':
                    self.returnPressed.emit()
                
                # Block the original key press
                return False
        
        keyboard.hook(callback)
        
        # Keep the hook running
        while self.hook_running:
            sleep_for(100)
    
    def closeEvent(self, event):
        self.hook_running = False
        keyboard.unhook_all()
        super().closeEvent(event)
    
    def check_if_tool_moved(self):

        if self.main_tool.x() != self.x() or (self.main_tool.y() != self.y() and self.is_not_visible):
            self.hide(animation=True)

        # Keep running itself
        QTimer.singleShot(50, self.check_if_tool_moved)

    def hide(self, animation=True):
        # Closing animation 
        self.is_not_visible = True
        if animation:
            self.anim.setStartValue(QRect(self.x(), self.y(), self.width(), self.textbox_height))
            self.anim.setEndValue(QRect(self.main_tool.x(), self.main_tool.y(), self.main_tool.width(), self.textbox_height))
            self.anim.start()
            sleep_for(300)

        self.clear()
        super().hide()

    def show(self):
        super().show()
        self.is_not_visible = False
        # self.setText()
        # Opening animation
        # Remove focus from other windows and focus only on main_tool

        # self.setFocus(Qt.OtherFocusReason)
        # self.setFocus()

        self.anim.setStartValue(QRect(self.main_tool.x(), self.main_tool.y(), self.main_tool.width(), self.textbox_height))
        self.anim.setEndValue(QRect(self.main_tool.x(), self.main_tool.y() - self.distance_from_tool, self.main_tool.width(), self.textbox_height))
        self.anim.start()

    def disappear(self):
        super().hide()

    def appear(self):
        super().show()

    def process_command(self, command):
        processor = CommandProcessor(self.main_tool)
        processor.process(command)

class FloatingLabel(QLabel):
    def __init__(self, main_tool, text):
        super().__init__(text)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()
        self.main_tool = main_tool

        # Create the animation
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)  # 1 = QEasingCurve.InOutQuad

        # Set Geometry and start the animation
        self.label_height = 60
        self.label_width = 60
        self.distance_from_tool = self.label_height + 10
        self.setGeometry(main_tool.x() - (self.label_width // 2) + (main_tool.width() // 2), 
                         main_tool.y(), self.label_width, self.label_height)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setStyleSheet(""" 
            QLabel {
                font-size: 24px;
                text-align: center;
            }
        """)
        self.setAlignment(Qt.AlignCenter)

    def present(self):
        self.show()
        self.is_not_visible = False
        # self.setText()
        # Opening animation
        self.anim.setStartValue(QRect(self.x(), self.y(), self.width(), self.height()))
        self.anim.setEndValue(QRect(self.x(), self.main_tool.y() - self.distance_from_tool, self.width(), self.height()))
        self.anim.start()
        # Wait for some time before calling it back
        sleep_for(500)
        self.hide()

class CommandProcessor():
    def __init__(self, main_tool):
        self.main_tool = main_tool

    def process(self, command):
        # Add Any Functionality to Assistant Commands using if-else
        if not command: pass

        elif os.path.exists('assistant_files.json'):
            with open('assistant_files.json', 'r') as f:
                commands = json.load(f)
                for text, path in commands.items():
                    if command == text:
                        os.startfile(path)
                        return
                
        if command.startswith('/'):
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            url = "https://chatgpt.com"
            subprocess.Popen([chrome_path, url])

            # Locate chatgpt image
            start_time = time.time()
            chatgpt_icon = 'images/chatgpt.png'
            if not os.path.exists(chatgpt_icon):
                sleep_for(2000)
            else:
                while time.time() - start_time < 10:
                    try:
                        pyautogui.locateOnScreen(chatgpt_icon, confidence=0.95, grayscale=True, 
                                                 region=[0, 0, pyautogui.size()[0], 100])
                    except:
                        sleep_for(100)
            pyautogui.typewrite(command[1:])

        elif command == 'exit':
            QApplication.quit()     # Quick and Clean exit

        else:   # The command is Unknown in this case
            label = FloatingLabel(self.main_tool, '❔')
            label.present()