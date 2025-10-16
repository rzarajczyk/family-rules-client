import logging

from osutils import get_os, OperatingSystem


class RunningApplications:
    @staticmethod
    def get_running_apps():
        match get_os():
            case OperatingSystem.MAC_OS:
                return set(RunningApplications.__get_running_apps_mac_os().keys())
            case OperatingSystem.WINDOWS:
                return set(RunningApplications.__get_running_apps_windows().keys())
            case _:
                raise Exception("Unsupported operating system")

    @staticmethod
    def __get_running_apps_windows():
        import win32gui
        import win32process
        import psutil
        import ctypes

        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid is not None:
            try:
                path = psutil.Process(pid).exe()
                return {path: pid}
            except Exception as e:
                logging.warning(f"Error during checking the path of running application with PID {{pid}}", e)
                return {}
        else:
            return {}

    @staticmethod
    def __get_running_apps_mac_os():
        from AppKit import NSWorkspace
        app = NSWorkspace.sharedWorkspace().frontmostApplication()
        # name = app.localizedName()
        path = app.executableURL().path()
        pid = app.processIdentifier()

        if path is not None and pid is not None:
            return {path: pid}
        else:
            return {}