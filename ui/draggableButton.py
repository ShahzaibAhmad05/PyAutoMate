# PyQt5 imports
from PyQt5.QtWidgets import QPushButton, QMessageBox, QFileDialog, QMenu, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# python libraries
import os, shutil, mouse, keyboard

# self-defined modules
from modules.sysUtils import sleep_for
from modules.styling import context_menu_stylesheet
from modules.utils import (add_spaces_for_context_menu, delete_script, 
                           load_script, save_script, generateRandomID)
from modules.getters import get_icon_path
from modules.interpreter import interpret

# UI elements
from ui.scriptEditorWindow import ScriptEditorWindow


class DraggableButton(QPushButton):
    def __init__(self, mainTool, scriptID):
        super().__init__(mainTool)

        self.mainTool = mainTool
        self.scriptID = scriptID

        # behaviour-control var
        self.dragging = False
        self.position = (0, 0)
        self.keyRef = None      # reference for the current key
        self.key = None         # the current shortcut key, e.g. Ctrl+Alt+E

        # setup button attributes using refresh
        self.refresh()

        # additional setup
        self.setObjectName("QPushButton")
        self.mouseDoubleClickEvent = self.run_script

    def editScript(self) -> None:
        """ allows the user to edit the script """
        scriptEditorWindow = ScriptEditorWindow(mainTool=self.mainTool, code=self.code, 
                            existing_image=get_icon_path(self.iconID), 
                            completionSignal=self.completionSignal)
        self.mainTool.hide()

        if scriptEditorWindow.exec_() == QDialog.Accepted:

            # update the attributes of the current button
            self.iconID, self.code, self.completionSignal = scriptEditorWindow.get_input()
            # save the updated script
            save_script(scriptID=self.scriptID, iconID=self.iconID, key=self.key, 
                        code=self.code, completionSignal=self.completionSignal)
            self.refresh()

        self.mainTool.show()

    def deleteButton(self):
        if QMessageBox.question(self, 'PyAutoMate', 'Are you sure you want to delete this button?') == QMessageBox.Yes:
            # remove any bound key first
            if self.keyRef is not None: keyboard.remove_hotkey(self.keyRef)
            delete_script(self.scriptID, self.iconID)
            i, j = self.mainTool.get_row_col_by_pos(self.position)
            self.mainTool.occupancies[i][j] = False
            self.hide()
        else:
            # place the button back
            self.mainTool.check_snap(self, self.position)

    def refresh(self):
        """ refreshes the button's attributes from the saved script data """
        script_data = load_script(self.scriptID)        # load the script data
        self.code = script_data['code']
        self.iconID = script_data['iconID']
        if self.keyRef is not None: keyboard.remove_hotkey(self.keyRef)
        self.key = script_data['key']
        self.completionSignal = script_data['completionSignal']
        # update behaviour
        self.setIcon(QIcon(get_icon_path(self.iconID)))
        self.keyRef = keyboard.add_hotkey(self.key, self.run_script)

    def mousePressEvent(self, event):
        if self.mainTool.is_small and event.button() == Qt.LeftButton:
            # wait for the mouse button to be released
            while mouse.is_pressed('left'): sleep_for(25)
            self.run_script()
        else:
            self.position = self.pos()
            self.dragging = True
            self.drag_start_position = event.pos()

    def contextMenuEvent(self, event):
        if self.mainTool.is_small: return
        # initialize context menu
        menu = QMenu(self)

        # create options in the menu
        action1 = menu.addAction(add_spaces_for_context_menu("Run Script", self.key))
        menu.addSeparator()
        action2 = menu.addAction(add_spaces_for_context_menu("Edit Script", ''))
        action3 = menu.addAction(add_spaces_for_context_menu(
            "Add Icon" if self.iconID is None else 'Edit Icon', shortcut_key=''))
        action5 = None
        if self.iconID is not None:
            text_to_add = add_spaces_for_context_menu("Remove Icon", '')
            action5 = menu.addAction(text_to_add)
        menu.addSeparator()
        action6 = menu.addAction("Delete")

        context_menu_stylesheet(menu, self.mainTool)       # set stylesheet for context menu
        action = menu.exec_(self.mapToGlobal(event.pos()))  # run context menu
   
        if action == action1:
            self.run_script()

        elif action == action2:
            self.editScript()
            
        elif action == action3:
            image_path, _ = QFileDialog.getOpenFileName(
                                parent=self,
                                caption="Select An Image",
                                filter="Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff *.svg);;All Files (*)",
                                options=QFileDialog.Options())
            
            if not os.path.exists(image_path): return       # make sure we have a valid path
            # remove the old image
            if self.iconID is not None and os.path.exists(get_icon_path(self.iconID)): 
                os.remove(get_icon_path(self.iconID))

            # save the icon in the script
            self.iconID = generateRandomID()
            shutil.copy(image_path, get_icon_path(self.iconID))
            save_script(self.scriptID, self.iconID, self.code, self.completionSignal)
            self.refresh()      # refresh to apply changes

        elif action5 and action == action5:
            # remove the icon from script file
            save_script(self.scriptID, self.code, None, self.completionSignal)
            self.refresh()
            
        elif action == action6:
            self.deleteButton()

    """ Functions that are not to be touched for now """

    def run_script(self):
        interpret(self.mainTool, commands=self.code, completionSignal=self.completionSignal)

    def mouseMoveEvent(self, event):
        if self.dragging:  # Allow movement only if dragging is active and not snapped
            self.move(self.mapToParent(event.pos() - self.drag_start_position))

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            # Check if the button should snap
            self.mainTool.check_snap(self, self.position)
            