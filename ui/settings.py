# PyQt5 imports
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QPushButton, QDialog, QVBoxLayout, QSpinBox
from PyQt5.QtCore import Qt

# python libraries
import json

# self-defined modules
from modules.styling import dialog_window_stylesheet
from modules.utils import enableDragging

# UI elements
from ui.toggleSwitch import ToggleSwitch

class Settings(QDialog):
    def __init__(self, mainTool):
        super().__init__(mainTool)
        self.mainTool = mainTool

        self.setWindowTitle('Configure App')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setFixedWidth(self.mainTool.app_size * 7)  # Adjust as needed

        title_bar_widget = dialog_window_stylesheet(self, self.mainTool)
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_widget.setLayout(main_layout)

        def label_stylesheet(widget):
            widget.setStyleSheet(" font-size: 16px; ")

        # size setting
        self.app_size_label = QLabel('size', self)
        self.app_size_spinbox = QSpinBox(self)
        self.app_size_spinbox.setFixedSize(
            int(self.mainTool.app_size * 1.25), 
            int(self.mainTool.app_size * 0.5))
        self.app_size_spinbox.setRange(30, 80)
        self.app_size_spinbox.setValue(self.mainTool.app_size)

        # grid setting
        self.app_grid_label = QLabel('grid', self)
        self.app_grid_spinbox = QSpinBox(self)
        self.app_grid_spinbox.setFixedSize(
            int(self.mainTool.app_size * 1.25), 
            int(self.mainTool.app_size * 0.5))
        self.app_grid_spinbox.setRange(4, 12)
        self.app_grid_spinbox.setValue(self.mainTool.app_grid)

        # dark mode setting
        self.dark_mode_label = QLabel("Dark Mode")
        self.dark_mode_toggle = ToggleSwitch(self.mainTool, initial_state=self.mainTool.app_theme == 'dark')
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

        # add widgets to layout
        app_size_widget = self.create_horizontal_layout(self.app_size_label, self.app_size_spinbox)
        main_layout.addWidget(app_size_widget)
        app_grid_widget = self.create_horizontal_layout(self.app_grid_label, self.app_grid_spinbox)
        main_layout.addWidget(app_grid_widget)
        dark_mode_widget = self.create_horizontal_layout(self.dark_mode_label, self.dark_mode_toggle)
        main_layout.addWidget(dark_mode_widget)
        main_layout.addWidget(self.space_label)
        main_layout.addWidget(self.cancel_button)
        main_layout.addWidget(self.ok_button)

        # define the overall layout
        overall_layout = QVBoxLayout(self)
        overall_layout.addWidget(title_bar_widget)
        overall_layout.addWidget(main_widget)
        self.setLayout(overall_layout)
        enableDragging(self)       # enables the dragging for this QDialog
        
    def save_settings(self) -> None:
        with open('settings.json', 'w') as file:
            app_settings = {
                'theme': 'dark' if self.dark_mode_toggle.isChecked() else 'light',
                'size': self.app_size_spinbox.value(),
                'grid': self.app_grid_spinbox.value()
            }
            json.dump(app_settings, file, indent=4)

    def create_horizontal_layout(self, widget_1, widget_2) -> QWidget:
        double_widget = QWidget(self)
        double_layout = QHBoxLayout(double_widget)
        double_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra margins
        double_layout.setSpacing(10)  # Adjust spacing between widgets
        double_widget.setLayout(double_layout)
        double_layout.addWidget(widget_1)
        double_layout.addWidget(widget_2)
        return double_widget
    