from osutils import get_os, SupportedOs


class RunningApplications:
    @staticmethod
    def get_running_apps():
        match get_os():
            case SupportedOs.MAC_OS:
                return set(RunningApplications.__get_running_apps_mac_os().keys())
            case SupportedOs.WINDOWS:
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
            name = psutil.Process(pid).exe()
            return {name: pid}
        else:
            return {}

    @staticmethod
    def __get_running_apps_mac_os():
        from AppKit import NSWorkspace
        app = NSWorkspace.sharedWorkspace().frontmostApplication()
        name = app.localizedName()
        pid = app.processIdentifier()

        if name is not None and pid is not None:
            return {name: pid}
        else:
            return {}