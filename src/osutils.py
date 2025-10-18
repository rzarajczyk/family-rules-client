import logging
import os
import platform
import sys
from enum import Enum, auto
from pathlib import Path

from Basedir import Basedir


class OperatingSystem(Enum):
    MAC_OS = auto()
    WINDOWS = auto()
    OTHER = auto()


def app_version():
    with open(Basedir.get() / "resources" / "version.txt", "r") as f:
        return f.read()


def get_os() -> OperatingSystem:
    current_platform = platform.platform().lower()
    if "windows" in current_platform:
        return OperatingSystem.WINDOWS
    elif "macos" in current_platform:
        return OperatingSystem.MAC_OS
    else:
        logging.error(f"Unsupported platform: {current_platform}")
        return OperatingSystem.OTHER


def is_dist() -> bool:
    # return True
    return getattr(sys, 'frozen', False)


def dist_path() -> Path:
    match get_os():
        case OperatingSystem.MAC_OS:
            if not is_dist():
                return Basedir.get().parent / "dist" / "FamilyRules.app"
            return Path(Basedir.get_str().removesuffix("/Contents/Frameworks"))
        case OperatingSystem.WINDOWS:
            # return Path("C:\\Program Files\\Family Rules\\FamilyRules.exe")
            if not is_dist():
                return Basedir.get().parent / "dist" / "FamilyRules.exe"
            return Path(sys.executable)
        case _:
            raise Exception("Unsupported operating system")


def app_data() -> Path:
    if not is_dist():
        return Basedir.get().parent / "data"

    match get_os():
        case OperatingSystem.MAC_OS:
            path = Path(Path.home(), "Library", "FamilyRules")
            path.mkdir(exist_ok=True)
            return path
        case OperatingSystem.WINDOWS:
            path = Path(os.getenv('LOCALAPPDATA'), "FamilyRules")
            path.mkdir(exist_ok=True)
            return path
        case _:
            raise Exception("Unsupported operating system")


def is_user_active() -> bool:
    """ user might be logged in, but inactive - when the "switch user" function was used """
    match get_os():
        case OperatingSystem.MAC_OS:
            return os.stat("/dev/console").st_uid == os.getuid()
        case OperatingSystem.WINDOWS:
            # FIXME UNSUPPORTED_WINDOWS
            logging.debug("Is user active - not implemented on Windows")
            return True
        case _:
            raise Exception("Unsupported operating system")


def make_sure_only_one_instance_is_running():
    if is_dist():
        match get_os():
            case OperatingSystem.MAC_OS:
                # FIXME UNSUPPORTED_MACOS
                pass
            case OperatingSystem.WINDOWS:
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

def open_folder(path: Path):
    match get_os():
        case OperatingSystem.MAC_OS:
            os.system(f'open "{path}"')
        case OperatingSystem.WINDOWS:
            os.startfile(path)
        case _:
            raise Exception("Unsupported operating system")