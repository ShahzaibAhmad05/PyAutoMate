from PyQt5.QtGui import QIcon, QTextCharFormat, QSyntaxHighlighter, QColor, QPainter, QCursor, QFont
from PyQt5.QtWidgets import (QPushButton,
                            QDialog, QMessageBox, QVBoxLayout, QHBoxLayout,
                            QTextEdit, QFileDialog, QRadioButton,
                            QButtonGroup, QMenu, QInputDialog, QLineEdit,
                            QCheckBox, QSpinBox)
from PyQt5.QtCore import QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap

def context_menu_stylesheet(widget, main_tool):
    widget.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
    widget.setAttribute(Qt.WA_TranslucentBackground)
    font = QFont("Arial", 10)
    widget.setFont(font)
    
    style_sheet_file = 'stylesheets/STL_context_menu.css' if main_tool.app_theme == 'light' else 'stylesheets/STD_context_menu.css'
    with open(style_sheet_file, 'r') as file:
        widget.setStyleSheet(file.read())

def dialog_window_stylesheet(dialog_window, main_tool):
    # Create title and close button
    title_label = QLabel(dialog_window.windowTitle())
    title_label.setObjectName("title-label")
    close_button = QPushButton("X")
    close_button_size = int(main_tool.app_size / 1.75)
    close_button.setFixedSize(close_button_size, close_button_size)
    close_button.setObjectName("close-button")
    close_button.clicked.connect(dialog_window.reject)

    # Layout for title bar
    Hlayout = QHBoxLayout()
    Hlayout.addWidget(title_label)
    Hlayout.addWidget(close_button, alignment=Qt.AlignRight)
    title_bar_widget = QWidget(dialog_window)
    title_bar_widget.setLayout(Hlayout)

    style_sheet_file = 'stylesheets/STL_dialog.css' if main_tool.app_theme == 'light' else 'stylesheets/STD_dialog.css'
    with open(style_sheet_file, 'r') as file:
        dialog_window.setStyleSheet(file.read())
    return title_bar_widget

def push_button_stylesheet(button, main_tool):
    style_sheet_file = 'stylesheets/STL_button.css' if main_tool.app_theme == 'light' else 'stylesheets/STD_button.css'
    with open(style_sheet_file, 'r') as file:
        button.setStyleSheet(file.read())

def push_button_disabled_stylesheet(button, main_tool):
    style_sheet_file = 'stylesheets/STL_button_disabled.css' if main_tool.app_theme == 'light' else 'stylesheets/STD_button_disabled.css'
    with open(style_sheet_file, 'r') as file:
        button.setStyleSheet(file.read())
