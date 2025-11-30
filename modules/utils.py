# PyQt5 imports
from PyQt5.QtCore import Qt, QPoint

# python libraries
import json, os, pyautogui, random

# self-defined functions
from modules.getters import get_script_path, get_icon_path

def save_script(scriptID: int | str, iconID: int | str, key: str, code: list, completionSignal: bool) -> None:
    """ saves a script to its corresponding JSON file """
    script_data = {
        "scriptID": scriptID,
        "iconID": iconID,
        "key": key,
        "code": code,
        "completionSignal": completionSignal
    }
    with open(get_script_path(scriptID), 'w') as file:
        json.dump(script_data, file, indent=4)

def delete_script(scriptID: int | str, iconID: int | str) -> None:
    """ removes a script JSON file """
    if os.path.exists(get_icon_path(iconID)):
        os.remove(get_icon_path(iconID))
    if os.path.exists(get_script_path(scriptID)):
        os.remove(get_script_path(scriptID))

def load_script(scriptID: int | str) -> dict:
    """ loads a script from its corresponding JSON file """
    with open(get_script_path(scriptID), 'r') as file:
        script_data = json.load(file)
    return script_data

def enableDragging(widget):
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
            x = max(0, min(widget.x(), pyautogui.size()[0] - widget.width()))
            y = max(0, min(widget.y(), pyautogui.size()[1] - widget.height()))
            widget.move(x, y)
            event.accept()

    widget.mousePressEvent = mousePressEvent
    widget.mouseMoveEvent = mouseMoveEvent
    widget.mouseReleaseEvent = mouseReleaseEvent

def generateRandomID() -> int:
    """ generates a random unused id """
    while True:
        id = random.randint(100000, 999999)
        if (not os.path.exists(get_icon_path(id)) and
            not os.path.exists(get_script_path(id))):
            return id

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

