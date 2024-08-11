import os
import plistlib
import subprocess
import sys
import time
from enum import Enum, auto
from pathlib import Path


class SupportedOs(Enum):
    MAC_OS = auto()
    UNSUPPORTED = auto()


def get_os() -> SupportedOs:
    if os.uname().sysname == 'Darwin':
        return SupportedOs.MAC_OS
    else:
        return SupportedOs.UNSUPPORTED


#
# def is_mac() -> bool:
#     return os.uname().sysname == 'Darwin'
#
#
# def is_linux() -> bool:
#     return os.uname().sysname == 'Linux'
#
#
# def is_windows() -> bool:
#     return os.uname().sysname == 'Windows'


def is_dist() -> bool:
    return getattr(sys, 'frozen', False)


def dist_path(basedir) -> Path:
    match get_os():
        case SupportedOs.MAC_OS:
            if not is_dist():
                return Path("/Users/rafal/Developer/family-rules-client/dist/Family Rules.app")
            return Path(basedir.removesuffix("/Contents/Frameworks"))
        case SupportedOs.UNSUPPORTED:
            raise Exception("Unsupported operating system")


def app_data() -> Path:
    if not is_dist():
        return Path("/Users/rafal/Developer/family-rules-client/data")
    match get_os():
        case SupportedOs.MAC_OS:
            path = Path(Path.home(), "Library", "Family Rules")
            path.mkdir(exist_ok=True)
            return path
        case SupportedOs.UNSUPPORTED:
            raise Exception("Unsupported operating system")


def path_to_str(path: Path) -> str:
    if path is None:
        return None
    return path.absolute().as_posix()


def is_user_active() -> bool:
    match get_os():
        case SupportedOs.MAC_OS:
            return os.stat("/dev/console").st_uid == os.getuid()
        case SupportedOs.UNSUPPORTED:
            raise Exception("Unsupported operating system")