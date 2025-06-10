from PyQt5.QtWidgets import QLineEdit, QApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
import subprocess, webbrowser, sys, os
import keyboard
import threading
import time
import string
from Universal import sleep_for
import pyautogui

class GlobalTextBox(QLineEdit):
    def __init__(self, main_tool):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.stop_flag = False

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        if main_tool.app_theme == 'dark':
            self.setStyleSheet("""
                QLineEdit { 
                    padding: 6px; 
                    font-size: 18px;
                    border-radius: 12px;
                    font-family: "Open Sans", Arial, sans-serif;
                    background-color: rgb(35, 35, 35);
                    border: 1px solid rgb(58, 58, 58);
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
                    border: 1px solid rgb(224, 224, 224);
                    color: rgb(0, 0, 0); 
                }
            """)
        
        # style_sheet_file = 'stylesheets/STL_dialog.css' if main_tool.app_theme == 'light' else 'stylesheets/STD_dialog.css'
        # with open(style_sheet_file, 'r') as file:
        #     self.setStyleSheet(file.read())
        self.main_tool = main_tool
        self.setMinimumHeight(40)
        self.update_geometry()
        
        # It is hidden by default
        # self.show()
        # self.activate_self()
        # Set up keyboard hook
        self.hook_running = False
        self.start_keyboard_hook()
        
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
            time.sleep(0.1)
    
    def closeEvent(self, event):
        self.hook_running = False
        keyboard.unhook_all()
        super().closeEvent(event)
    
    def update_geometry(self):
        # Algorithms for calculating positions
        y = self.main_tool.y() - self.height() - 10

        # Update geometry
        self.setGeometry(self.main_tool.x(), y, self.main_tool.width(), 40)

        # Keep running it afterwards
        QTimer.singleShot(50, self.update_geometry)

    def process_command(self):
        command = self.text()
        self.clear()
        if not command:
            pass
        else:
            import subprocess

            url = "https://www.google.com"
            user_data_dir = r"C:\Users\YourUser\AppData\Local\Google\Chrome\User Data"  # Windows

            subprocess.run([
                "chrome.exe",
                f"--user-data-dir={user_data_dir}",
                "--profile-directory=Default",
                url
            ], shell=True)

            print('opened someth')
