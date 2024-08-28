import getpass
import platform
import subprocess
from collections import defaultdict
from osutils import get_os, SupportedOs


class RunningApplications:
    def get_running_apps(self):
        match get_os():
            case SupportedOs.MAC_OS:
                return set(self.__get_running_apps_mac_os().keys())
            case SupportedOs.WINDOWS:
                return set(self.__get_running_apps_windows().keys())
            case _:
                raise Exception("Unsupported operating system")

    # def kill_by_name(self, app):
    #     match get_os():
    #         case SupportedOs.MAC_OS:
    #             apps = self.__get_running_apps_mac_os()
    #             pids = apps[app]
    #             for pid in pids:
    #                 try:
    #                     os.kill(pid, signal.SIGTERM)
    #                 except Exception as e:
    #                     pass
    #         case _:
    #             raise Exception("Unsupported operating system")

    def __get_running_apps_windows(self):
        import win32gui
        import win32process
        import psutil

        def enum_window_callback(hwnd, process_windows):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process_windows.add(pid)

        process_windows = set()
        win32gui.EnumWindows(enum_window_callback, process_windows)
        grouped_processes = defaultdict(list)
        expected_username = platform.node() + "\\" + getpass.getuser()
        for p in psutil.process_iter(['pid', 'username', 'exe']):
            if p.info["username"] == expected_username:
                if p.info["pid"] in process_windows:
                    if not p.info["exe"].startswith("C:\\Windows"):
                        grouped_processes[p.info["exe"]].append(p.info["pid"])
        return dict(grouped_processes)

    def __get_running_apps_mac_os(self):
        user = subprocess.run("whoami", capture_output=True, text=True).stdout.strip()
        result = subprocess.run(["ps", "-u", user, "-o", "pid,comm"], capture_output=True, text=True)

        output = result.stdout.strip().split('\n')

        header = output[0]
        data_lines = output[1:]
        columns = [col.strip() for col in header.split()]

        processes = []
        for line in data_lines:
            values = [val.strip() for val in line.split(None, 1)]
            process_info = dict(zip(columns, values))
            processes.append(process_info)

        processes = [process for process in processes if process['COMM'].startswith("/Applications/")]
        for process in processes:
            process['COMM'] = process['COMM'][:process['COMM'].index(".app/") + 4]
            process['COMM'] = process['COMM'].removeprefix("/Applications/")
            process['PID'] = int(process['PID'])

        grouped_processes = defaultdict(list)
        for entry in processes:
            comm = entry['COMM']
            pid = entry['PID']
            grouped_processes[comm].append(pid)
        grouped_processes = dict(grouped_processes)

        return grouped_processes
