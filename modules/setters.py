import json

def set_settings(app_settings: dict) -> None:
    """ saves the app settings to settings.json """
    with open('settings.json', 'w') as file:
        json.dump(app_settings, file, indent=4)