import os
import sys
from pathlib import Path


def is_mac() -> bool:
    return os.uname().sysname == 'Darwin'


def is_linux() -> bool:
    return os.uname().sysname == 'Linux'


def is_windows() -> bool:
    return os.uname().sysname == 'Windows'


def is_dist() -> bool:
    return getattr(sys, 'frozen', False)


def dist_path(basedir) -> Path:
    if not is_dist():
        return None
    if is_mac():
        return Path(basedir.removesuffix("/Contents/Frameworks"))
    else:
        raise Exception("Unsupported OS")



def app_data() -> Path:
    if is_mac():
        path = Path(Path.home(), "Library", "Family Rules")
        path.mkdir(exist_ok=True)
        return path
    else:
        raise Exception("Unsupported OS")


def path_to_str(path: Path) -> str:
    if path is None:
        return None
    return path.absolute().as_posix()

