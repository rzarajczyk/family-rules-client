import logging
import os
import platform
import sys
from enum import Enum, auto
from pathlib import Path

from basedir import Basedir


class SupportedOs(Enum):
    MAC_OS = auto()
    WINDOWS = auto()
    UNSUPPORTED = auto()


def app_version():
    with open(Basedir.get() / "resources" / "version.txt", "r") as f:
        return f.read()


def get_os() -> SupportedOs:
    if "windows" in platform.platform().lower():
        return SupportedOs.WINDOWS
    elif os.uname().sysname == 'Darwin':  ## TODO migrate to pltform
        return SupportedOs.MAC_OS
    else:
        return SupportedOs.UNSUPPORTED


def is_dist() -> bool:
    # return True
    return getattr(sys, 'frozen', False)


def dist_path() -> Path:
    match get_os():
        case SupportedOs.MAC_OS:
            if not is_dist():
                return Basedir.get().parent / "dist" / "FamilyRules.app"
            return Path(Basedir.get_str().removesuffix("/Contents/Frameworks"))
        case SupportedOs.WINDOWS:
            if not is_dist():
                return Basedir.get().parent / "dist" / "FamilyRules.exe"
            return Path(sys.executable)
        case _:
            raise Exception("Unsupported operating system")


def app_data() -> Path:
    if not is_dist():
        return Basedir.get().parent / "data"

    match get_os():
        case SupportedOs.MAC_OS:
            path = Path(Path.home(), "Library", "FamilyRules")
            path.mkdir(exist_ok=True)
            return path
        case SupportedOs.WINDOWS:
            path = Path(os.getenv('LOCALAPPDATA'), "FamilyRules")
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


def make_sure_only_one_instance_is_running():
    if is_dist():
        match get_os():
            case SupportedOs.MAC_OS:
                # FIXME UNSUPPORTED_MACOS
                pass
            case SupportedOs.WINDOWS:
                import psutil
                import platform
                import getpass

                expected_username = platform.node() + "\\" + getpass.getuser()
                count = 0
                for p in psutil.process_iter(['username', 'exe']):
                    if p.info["username"] == expected_username:
                        if p.info['exe'].endswith(dist_path().name):
                            count += 1
                if count > 1:
                    logging.warning("Detected another instance running - quitting!")
                    sys.exit(0)
            case _:
                raise Exception("Unsupported operating system")
