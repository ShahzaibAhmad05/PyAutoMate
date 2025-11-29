# PyQt5 imports
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QIcon

# python libraries
import os, sys

# self-defined modules
from modules.sysUtils import close_other_instances
from modules.getters import get_logo_path
from mainTool import MainTool


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
    root_app = QApplication([])
    close_other_instances()
    root_app.setWindowIcon(QIcon(get_logo_path()))

    main_tool = MainTool()
    main_tool.show() # finally, show the main tool

    root_app.exec_()   # should never exit from here
    sys.exit(1)

if __name__ == "__main__":
    main()