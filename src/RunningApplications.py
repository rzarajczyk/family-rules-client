import os
import signal
import subprocess
from collections import defaultdict

from osutils import is_mac


class RunningApplications:
    def get_running_apps(self):
        if is_mac():
            return set(self.__get_running_apps_mac_os().keys())
        else:
            raise Exception("Unsupported operating system")

    def kill_by_name(self, app):
        if is_mac():
            apps = self.__get_running_apps_mac_os()
            pids = apps[app]
            for pid in pids:
                try:
                    os.kill(pid, signal.SIGTERM)
                except Exception as e:
                    pass
        else:
            raise Exception("Unsupported operating system")

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
