import json

from osutils import app_data

CURRENT = 1


class Settings:
    __instance: 'Settings' = None

    def __init__(self, server, username, instance_name, instance_token):
        self.server = server
        self.username = username
        self.instance_name = instance_name
        self.instance_token = instance_token

    def to_json(self):
        return {
            'server': self.server,
            'username': self.username,
            'instance_name': self.instance_name,
            'instance_token': self.instance_token,
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
                instance_name=json_settings['instance_name'],
                instance_token=json_settings['instance_token']
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
    def create(server, username, instance_name, instance_token):
        settings = Settings(server, username, instance_name, instance_token)
        Settings.save(settings)

    @staticmethod
    def migrate(json_settings: dict) -> tuple[dict, bool]:
        v = json_settings.get('_version', 0)
        if v == CURRENT:
            return json_settings, False

        if v == 0:
            pass
        return json_settings, True
