# PyQt5 imports
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer, QEventLoop

# python libraries
import psutil, sys, os

def close_other_instances():
    """ no args, closes all the other instances of the current process """
    current_process = psutil.Process(os.getpid())
    current_name = current_process.name()
    # Check all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == current_name and proc.info['pid'] != current_process.pid:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except TimeoutError:
                QMessageBox.critical(None, 'PyAutoMate', 'An unexpected error occured. '
                        'Please contact the developer if the issue persists.')
                sys.exit(1)

def sleep_for(sleep_time: int) -> None:
    """ 
    Calls a sleep event without blocking the app's loop.
    Args:
        sleep_time (int): requires time given in ms.
    """
    loop = QEventLoop()
    QTimer.singleShot(sleep_time, loop.quit)    # assuming sleep_time is in ms
    loop.exec_()
