import json
from enum import Enum, auto

from osutils import app_data

class UptimeMethod(Enum):
    PS = auto()
    APPLE_SCREEN_TIME = auto()


class Settings:
    def __init__(self, json_settings):
        self.server = json_settings['server']
        self.username = json_settings['username']
        self.instance_name = json_settings['instance_name']
        self.instance_token = json_settings['instance_token']
        self.uptime_method = UptimeMethod.PS

    @staticmethod
    def setup_completed():
        file = app_data() / "settings.json"
        return file.exists()

    @staticmethod
    def load() -> 'Settings':
        file = app_data() / "settings.json"
        with open(file, "r") as f:
            json_settings = json.load(f)
        return Settings(json_settings)

    @staticmethod
    def create(server, username, instance_name, instance_token):
        json_settings = dict()
        json_settings['server'] = server
        json_settings['username'] = username
        json_settings['instance_name'] = instance_name
        json_settings['instance_token'] = instance_token

        file = app_data() / "settings.json"
        if file.exists():
            raise Exception("Settings file already exists")
        with open(file, 'w') as f:
            json.dump(json_settings, f, indent=4)