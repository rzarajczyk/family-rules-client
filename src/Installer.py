import logging
import os
import shutil
import time
from pathlib import Path

from Settings import Settings
from osutils import is_mac


class Installer:

    @staticmethod
    def do_server_login(server, username, password, instance_name) -> str:
        time.sleep(3)
        return "ssss"

    @staticmethod
    def save_settings(server, username, instance, token):
        Settings.create(server, username, instance, token)

    @staticmethod
    def install_autorun(basedir):
        if is_mac():
            agents = os.path.join(Path.home(), "Library", "LaunchAgents")
            file = Path(agents, "pl.zarajczyk.family-rules-client.plist")
            if not file.is_file():
                plist = Path(basedir, "resources", "pl.zarajczyk.family-rules-client.plist")
                shutil.copy(plist, file)
                logging.info(f"plist file installed")
        else:
            raise Exception("Unsupported OS")
