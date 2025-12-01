# PyQt5 imports
from PyQt5.QtWidgets import QMessageBox

# python libraries
import os, time, pyautogui, keyboard, mouse, webbrowser, subprocess
from io import BytesIO
from PIL import Image
from pygetwindow import getWindowsWithTitle

# self-defined modules
from modules.sysUtils import sleep_for
from modules.utils import decodeVar
from modules.getters import get_icon_path


""" interpreter function """

def interpret(mainTool, commands: list[list], completionSignal: bool=False) -> None:
    """
    takes in a list of interpreter readable commands with the proper format to execute them.
    Command[0]: the type of the command
    Command[1]: the specification of the type

    param: parent is a widget on which the dialogs would be set
    param: commands is a list of lists, where each list represents a command
    param: variables (dict)
    param: completionSignal if true, provides a signal on completion of the script, false by default
    param: dialogs_parent (ptr) points to the window hosting the dialogs, i.e. small tool

    """
    mainTool.hide()
    sleep_for(100)
    if commands == None: return     # safety check

    for command in commands:

        # if command is empty or just a \n
        if not command: pass

        # for mouse clicks
        elif command[0] == 'click':

            # the click type, left, right, or double
            if decodeVar(command[1]) == 'left': click_function = pyautogui.leftClick
            elif decodeVar(command[1]) == 'right': click_function = pyautogui.rightClick
            elif decodeVar(command[1]) == 'double': click_function = pyautogui.doubleClick

            # click by coordinates
            if command[2] == 'coord':
                x = decodeVar(command[3])
                y = decodeVar(command[4])
                click_function(x, y)

            # click by image, also requires timeout
            elif command[2] == 'img':
                timeout = decodeVar(command[3])
                # load the image
                image_path = get_icon_path(decodeVar(command[4]))
                with open(image_path, 'rb') as file:
                    image_data = file.read()

                x, y = find_image_location(image_data, timeout)
                if x and y:
                    click_function(x, y)
                else:
                    QMessageBox.critical(mainTool, 'PyAutoMate', f'The required image was not Found within {timeout} seconds')
                    break

        # for opening
        elif command[0] == 'open':

            # opening local files
            if command[1] == 'file':
                file_path = decodeVar(command[2])
                if os.path.exists(file_path):
                    os.startfile(file_path)
                else:
                    QMessageBox.critical(mainTool, 'PyAutoMate', f'{file_path} does not exist')

            # opening websites on default browser
            elif command[1] == 'link':
                link = decodeVar(command[2])
                webbrowser.open(link)

        # for waiting
        elif command[0] == 'wait':

            # for waiting for a specified time
            if command[1] == 'time':
                sleep_time = decodeVar(command[2]) * 1000
                sleep_for(sleep_time)

            # for waiting for a specific image to appear
            elif command[1] == 'img':
                timeout = decodeVar(command[2])
                image_path = get_icon_path(decodeVar(command[3]))
                with open(image_path, 'rb') as file:
                    image_data = file.read()

                if not find_image_location(image_data, timeout):
                    QMessageBox.critical(mainTool, 'PyAutoMate', f'The required image was not Found within {timeout} seconds')
                    break

            # for waiting for a button press
            elif command[1] == 'key':
                button = decodeVar(command[2])
                while not keyboard.is_pressed(button): sleep_for(25)
                while keyboard.is_pressed(button): sleep_for(25)

            # for waiting for a mouse press
            elif command[1] == 'click':
                button = decodeVar(command[3])
                while not mouse.is_pressed(button): sleep_for(25)
                while mouse.is_pressed(button): sleep_for(25)

        # for doing some keyboard type action
        elif command[0] == 'key':

            # for typing
            if command[1] == 'type':
                content = command[2]
                pyautogui.typewrite(content, interval=0.005)

            # for pressing hotkeys
            elif command[1] == 'press':
                button = command[2].split('+')   # assuming command[2] is a list
                pyautogui.hotkey(button)
                sleep_for(500)

        # for showing a window
        elif command[0] == 'show':
            window_title = command[1]
            show_window(window_title, mainTool)

        elif command[0] == 'cmd':
            cmd = command[1:]
            subprocess.run(cmd, shell=True)

    # optionally provide a completion signal
    if completionSignal:
        QMessageBox.information(mainTool, 'PyAutoMate', f'Script was executed successfully')

    mainTool.show()

""" interpreter helper functions """

def find_image_location(binary_data: str, timeout: float) -> tuple:
    """
    helper function for interpreter to find images on the screen, 
    confidence=0.99 by default. Returns x and y coordinates of 
    the found image location, if not found, returns a tuple of none, none
    """
    image = Image.open(BytesIO(binary_data))
    start_time = time.time()
    while True:
        try:
            location = pyautogui.locateOnScreen(image, confidence=0.99)
            if location:
                return location.left, location.top
        except pyautogui.ImageNotFoundException:
            if time.time() - start_time > timeout:
                return None, None

def show_window(window_title: str, parent, timeout: int=0) -> None:
    """ activates the running window with the given title """
    start_time = time.time()
    while True:
        windows = getWindowsWithTitle(window_title)
        if windows:
            win = windows[0]
            win.activate()
            win.maximize()
            break
        elif time.time() - start_time > timeout:
            QMessageBox.critical(parent, 'PyAutoMate', f'Window with title {window_title} was not found')
            break
