from PyQt5.QtWidgets import QPushButton

class ToggleSwitch(QPushButton):
    def __init__(self, mainTool, initial_state=False) -> None:
        """ 
        Initializes a QPushButton which is a toggle. Use isChecked() method to 
        check if the button is on.

        Args:
            parent (QWidget): the parent of the button.
            initial_state (bool: False): the initial state of the button.
        """
        super().__init__(mainTool)
        self.mainTool = mainTool
        
        self.setCheckable(True)  # Ensures button can be toggled
        self.setFixedSize(int(self.mainTool.app_size * 1.25), int(self.mainTool.app_size * 0.5))
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
