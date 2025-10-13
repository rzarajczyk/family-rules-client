import json
import logging

import requests
from requests.auth import HTTPBasicAuth

from osutils import app_data

CURRENT = 3


class Settings:
    __instance: 'Settings' = None

    def __init__(self, server, username, instance_id, instance_name, instance_token, language):
        self.server = server
        self.username = username
        self.instance_id = instance_id
        self.instance_name = instance_name
        self.instance_token = instance_token
        self.language = language

    def to_json(self):
        return {
            'server': self.server,
            'username': self.username,
            'instance_id': self.instance_id,
            'instance_name': self.instance_name,
            'instance_token': self.instance_token,
            'language': self.language,
            '_version': CURRENT
        }

    @staticmethod
    def setup_completed():
        file = app_data() / "settings.json"
        return file.exists()

    @staticmethod
    def load() -> 'Settings':
        if Settings.__instance is None:
            file = app_data() / "settings.json"
            with open(file, "r") as f:
                json_settings = json.load(f)
            json_settings, is_migrated = Settings.migrate(json_settings)
            Settings.__instance = Settings(
                server=json_settings['server'],
                username=json_settings['username'],
                instance_id=json_settings['instance_id'],
                instance_name=json_settings['instance_name'],
                instance_token=json_settings['instance_token'],
                language=json_settings['language']
            )
            if is_migrated:
                Settings.save(Settings.__instance)
        return Settings.__instance

    @staticmethod
    def save(settings: 'Settings'):
        settings_json = settings.to_json()
        file = app_data() / "settings.json"
        with open(file, 'w') as f:
            json.dump(settings_json, f, indent=4)

    @staticmethod
    def create(server, username, instance_id, instance_name, instance_token, language):
        settings = Settings(server, username, instance_id, instance_name, instance_token, language)
        Settings.save(settings)

    def update_language(self, language):
        """Update the language setting and save to file"""
        self.language = language
        Settings.save(self)

    @staticmethod
    def migrate(json_settings: dict) -> tuple[dict, bool]:
        v = json_settings.get('_version', 0)
        if v == CURRENT:
            return json_settings, False
        if v == 2:
            logging.warning(f"Migrating config from version {v}")
            json_settings['language'] = 'en'
            return json_settings, True
        if v == 1:
            logging.warning(f"Migrating config from version {v}")
            response = requests.post(
                url=f"{json_settings['server']}/api/v1/migrator/get-instance-id",
                data=json_settings['instance_name'],
                auth=HTTPBasicAuth(json_settings['username'], json_settings['instance_token'])
            )
            response.raise_for_status()
            json_settings['instance_id'] = response.text
            logging.warning(f"Fetched instance_id {json_settings['instance_id']}")
            return json_settings, True
        if v == 0:
            pass
        return json_settings, True
