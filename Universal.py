from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap
import logging
import os
import inspect
import pickle

def sleep_for(sleep_time: int) -> None:
    """ 
    Calls a sleep event without blocking the app's loop.
    Args:
        sleep_time (int): requires time given in ms.
    """
    loop = QEventLoop()
    QTimer.singleShot(sleep_time, loop.quit)    # assuming sleep_time is in ms
    loop.exec_()