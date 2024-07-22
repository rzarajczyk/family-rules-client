from gui import Gui
from osutils import is_mac


class Action:
    def execute(self, gui: Gui):
        pass


class NoAction(Action):
    pass


class LockScreen(Action):
    def execute(self, gui: Gui):
        if is_mac():
            from ctypes import CDLL
            login_pf = CDLL('/System/Library/PrivateFrameworks/login.framework/Versions/Current/login')
            login_pf.SACLockScreenImmediate()
        else:
            raise Exception("Unsupported operating system")


class Notify(Action):
    def execute(self, gui: Gui):
        gui.show_top_right_window()
        # gui.show_notification("hello", "notification")
