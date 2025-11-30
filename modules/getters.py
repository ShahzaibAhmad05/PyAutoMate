import json

def get_settings() -> dict:
    """ loads the app settings from settings.json """
    with open('settings.json', 'r') as file:
        app_settings = json.load(file)
    return app_settings

def get_logo_path() -> str:
    """ returns the path to the app logo """
    return 'logo.png'

def get_icon_path(iconID: int | str) -> str:
    """ returns the path to a given icon """
    if iconID == None: 
        return None
    return f'images/{iconID}.png'

def get_script_path(scriptID: int | str) -> str:
    """ returns the path to a given script """
    return f'scripts/{scriptID}.json'
