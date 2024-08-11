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
        self.uptime_method = UptimeMethod[json_settings['uptime_method']]

    def to_json(self):
        return {
            'server': self.server,
            'username': self.username,
            'instance_name': self.instance_name,
            'instance_token': self.instance_token,
            'uptime_method': self.uptime_method.name
        }

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
    def save(settings: 'Settings'):
        settings_json = settings.to_json()
        Settings.__save_json(settings_json)

    @staticmethod
    def __save_json(settings_json: dict):
        file = app_data() / "settings.json"
        with open(file, 'w') as f:
            json.dump(settings_json, f, indent=4)

    @staticmethod
    def create(server, username, instance_name, instance_token):
        settings_json = {
            'server': server,
            'username': username,
            'instance_name': instance_name,
            'instance_token': instance_token,
            'uptime_method': UptimeMethod.PS.name
        }
        Settings.__save_json(settings_json)
