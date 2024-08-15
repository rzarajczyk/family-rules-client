from datetime import datetime

from gui import Gui
from osutils import get_os, SupportedOs


class State:
    def __init__(self, json):
        self.locked_since = self.parse_date(json['lockedSince'])
        self.logged_out_since = self.parse_date(json['loggedOutSince'])

    def parse_date(self, date_string):
        return None if date_string is None else datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')

    @staticmethod
    def empty():
        return State({
            'lockedSince': None,
            'loggedOutSince': None
        })


class StateController:
    def __init__(self):
        self.gui: Gui = None
        self.state: State = State.empty()

    def initialize(self, gui: Gui):
        self.gui = gui

    def run(self, state: State):
        if state is not None:
            self.state = state

        now = datetime.now()
        if state.logged_out_since is not None and now >= state.logged_out_since:
            print("Logged out!")
            # if not self.gui.count_down_window.isVisible():
            #     self.gui.count_down_window.start(10)
        else:
            print("NOT Logged out!")
            # self.gui.count_down_window.stop()
            # self.__logout()
            # return

        if state.locked_since is not None and now >= state.locked_since:
            print("Locked")
            # self.gui.block_access_window.show()
        else:
            print("NOT Locked")
            # self.gui.block_access_window.hide()

    def __logout(self):
        match get_os():
            case SupportedOs.MAC_OS:
                from ctypes import CDLL
                login_pf = CDLL('/System/Library/PrivateFrameworks/login.framework/Versions/Current/login')
                login_pf.SACLockScreenImmediate()
            case SupportedOs.UNSUPPORTED:
                raise Exception("Unsupported operating system")

# class Action:
#     def execute(self, gui: 'Gui'):
#         pass
#
#
# class NoAction(Action):
#     pass
#
#
# class LockSystem(Action):
#     def execute(self, gui: 'Gui'):
#         match get_os():
#             case SupportedOs.MAC_OS:
#                 from ctypes import CDLL
#                 login_pf = CDLL('/System/Library/PrivateFrameworks/login.framework/Versions/Current/login')
#                 login_pf.SACLockScreenImmediate()
#             case SupportedOs.UNSUPPORTED:
#                 raise Exception("Unsupported operating system")
#
#
# class BlockAccess(Action):
#     def execute(self, gui: 'Gui'):
#         gui.block_access_window.show()
#
#
# class KillApplication(Action):
#     def __init__(self, appName: str):
#         self.appName = appName
#
#     def execute(self, gui: 'Gui'):
#         RunningApplications().kill_by_name(self.appName)
#
#
# class Notify(Action):
#     def execute(self, gui: "Gui"):
#         pass
#         # gui.show_top_right_window()
#         # gui.show_notification("hello", "notification")
