import os
from pathlib import Path


def is_mac() -> bool:
    return os.uname().sysname == 'Darwin'


def is_linux() -> bool:
    return os.uname().sysname == 'Linux'


def is_windows() -> bool:
    return os.uname().sysname == 'Windows'


def app_data() -> Path:
    if is_mac():
        path = Path(Path.home(), "Library", "Family Rules")
        path.mkdir(exist_ok=True)
        return path
    else:
        raise RuntimeError("Unsupported OS")
