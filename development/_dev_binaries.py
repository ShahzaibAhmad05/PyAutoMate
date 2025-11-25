import pickle
from PyQt5.QtGui import QIcon, QPixmap
import os
from development._dev_variables import data_file, app_version
import platform
import psutil
import json

"""
The structure of script.bin is as follows:
[[id, image_data, script_code, completion_signal]]

"""

if __name__ == "__main__":

    """ for testing purposes """
    app_settings = {
        'theme': 'light',
        'size': '45',
        'grid': '5'
    }
    logo_icon = None
    # with open('_dev_img/logo.png', 'rb') as file:
    #     logo_icon = file.read()
    # code = [[0, logo_icon, None, False]]

    with open('settings.json', 'w') as file:
        json.dump(app_settings, file, indent=4)
    # with open('script.bin', 'wb') as file:
    #     pickle.dump(code, file)