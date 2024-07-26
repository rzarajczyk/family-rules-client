import logging
import os.path
import shutil
from pathlib import Path

from osutils import is_mac


def check_install(basedir):
    if is_mac():
        agents = os.path.join(Path.home(), "Library", "LaunchAgents")
        file = Path(agents, "pl.zarajczyk.family-rules-client.plist")
        if not file.is_file():
            plist = Path(basedir, "resources", "pl.zarajczyk.family-rules-client.plist")
            shutil.copy(plist, file)
            logging.info(f"plist file installed")