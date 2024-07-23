from RunningApplications import RunningApplications
from osutils import is_mac


class Action:
    def execute(self, gui: 'Gui'):
        pass


class NoAction(Action):
    pass


class LockSystem(Action):
    def execute(self, gui: 'Gui'):
        if is_mac():
            from ctypes import CDLL
            login_pf = CDLL('/System/Library/PrivateFrameworks/login.framework/Versions/Current/login')
            login_pf.SACLockScreenImmediate()
        else:
            raise Exception("Unsupported operating system")


class BlockAccess(Action):
    def execute(self, gui: 'Gui'):
        gui.block_access_window.show()


class KillApplication(Action):
    def __init__(self, appName: str):
        self.appName = appName

    def execute(self, gui: 'Gui'):
        RunningApplications().kill_by_name(self.appName)


class Notify(Action):
    def execute(self, gui: "Gui"):
        pass
        # gui.show_top_right_window()
        # gui.show_notification("hello", "notification")
