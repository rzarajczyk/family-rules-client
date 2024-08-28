import logging
import os
import sys
from enum import Enum, auto
from pathlib import Path
import platform

from basedir import Basedir


class SupportedOs(Enum):
    MAC_OS = auto()
    WINDOWS = auto()
    UNSUPPORTED = auto()


def get_os() -> SupportedOs:
    if "windows" in platform.platform().lower():
        return SupportedOs.WINDOWS
    elif os.uname().sysname == 'Darwin': ## TODO migrate to pltform
        return SupportedOs.MAC_OS
    else:
        return SupportedOs.UNSUPPORTED


def is_dist() -> bool:
    return getattr(sys, 'frozen', False)


def dist_path() -> Path:
    basedir = Basedir.get_str()
    match get_os():
        case SupportedOs.MAC_OS:
            if not is_dist():
                return Path("/Users/rafal/Developer/family-rules-client/dist/Family Rules.app")
            return Path(basedir.removesuffix("/Contents/Frameworks"))
        case SupportedOs.WINDOWS:
            # FIXME UNSUPPORTED_WINDOWS
            logging.critical("Cannot determine dist_path on Windows - not implemented yet")
            return None
        case _:
            raise Exception("Unsupported operating system")


def app_data() -> Path:
    if not is_dist():
        return Basedir.get().parent / "data"

    match get_os():
        case SupportedOs.MAC_OS:
            path = Path(Path.home(), "Library", "Family Rules")
            path.mkdir(exist_ok=True)
            return path
        case SupportedOs.WINDOWS:
            path = Path(os.getenv('LOCALAPPDATA'), "Family Rules")
            path.mkdir(exist_ok=True)
            return path
        case _:
            raise Exception("Unsupported operating system")


def path_to_str(path: Path) -> str:
    if path is None:
        return None
    return path.absolute().as_posix()


def is_user_active() -> bool:
    match get_os():
        case SupportedOs.MAC_OS:
            return os.stat("/dev/console").st_uid == os.getuid()
        case SupportedOs.WINDOWS:
            # FIXME UNSUPPORTED_WINDOWS
            logging.debug("Is user active - not implemented on Windows")
            return True
        case _:
            raise Exception("Unsupported operating system")
