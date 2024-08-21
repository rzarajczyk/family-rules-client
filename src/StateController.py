from gui import Gui
from gui_countdown import CountDownState
from osutils import get_os, SupportedOs


class State:
    def __init__(self, json):
        self.device_state = json['deviceState']
        self.device_state_countdown = int(json['deviceStateCountdown'])

    @staticmethod
    def empty():
        return State({
            'deviceState': 'ACTIVE',
            'deviceStateCountdown': 0
        })


class StateController:
    def __init__(self):
        self.gui: Gui = None
        self.state: State = State.empty()
        self.countdown_done = False

    def initialize(self, gui: Gui):
        self.gui = gui

    def run(self, state: State):
        if state is not None:
            self.state = state

        match state.device_state:
            case "ACTIVE":
                self.gui.count_down_window.stop_reset()
                self.gui.block_access_window.hide()
            case "LOCKED":
                if self.gui.count_down_window.state.value == CountDownState.IN_PROGRESS.value and self.gui.count_down_window.name != "LOCKED":
                    self.gui.count_down_window.stop_reset()

                def lock():
                    self.gui.block_access_window.show()
                    self.gui.count_down_window.hide()

                if self.gui.count_down_window.state.value == CountDownState.NOT_STARTED.value:
                    self.gui.count_down_window.start(
                        initial_amount_seconds=self.state.device_state_countdown,
                        name="LOCKED",
                        onTimeout=lock)
            case "LOGGED_OUT":
                if self.gui.count_down_window.state.value == CountDownState.IN_PROGRESS.value and self.gui.count_down_window.name != "LOGGED_OUT":
                    self.gui.count_down_window.stop_reset()

                def lock():
                    self.gui.count_down_window.hide()
                    self.__logout()

                if self.gui.count_down_window.state.value == CountDownState.NOT_STARTED.value:
                    self.gui.count_down_window.start(
                        initial_amount_seconds=self.state.device_state_countdown,
                        name="LOGGED_OUT",
                        onTimeout=lock)
                elif self.gui.count_down_window.state.value == CountDownState.DONE.value:
                    self.__logout()
            case _:
                raise Exception(f"unsupported state: {state.device_state}")

    def __logout(self):
        match get_os():
            case SupportedOs.MAC_OS:
                from ctypes import CDLL
                login_pf = CDLL('/System/Library/PrivateFrameworks/login.framework/Versions/Current/login')
                login_pf.SACLockScreenImmediate()
            case SupportedOs.WINDOWS:
                import ctypes
                ctypes.windll.user32.LockWorkStation()
            case _:
                raise Exception("Unsupported operating system")