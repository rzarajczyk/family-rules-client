import logging
from osutils import get_os, OperatingSystem

class Beep:
    def beep(self):
        pass
    @staticmethod
    def instance():
        match get_os():
            case OperatingSystem.MAC_OS:
                return MacOsBeep()
            case OperatingSystem.WINDOWS:
                return WinBeep()
            case _:
                raise Exception("Unsupported operating system")

class MacOsBeep(Beep):
    def beep(self):
        try:
            from subprocess import Popen, DEVNULL
            Popen(["osascript", "-e", "beep"], stdout=DEVNULL, stderr=DEVNULL)
        except Exception as e:
            logging.warning(f"Unable to play a sound: {e}")

class WinBeep(Beep):
    def beep(self):
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception as e:
            logging.warning(f"Unable to play a sound: {e}")