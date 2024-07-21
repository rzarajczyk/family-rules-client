import os
import subprocess


class RunningApplicationsFetcher:
    def get_running_apps(self):
        if self.__is_mac_os():
            return self.__get_running_apps_mac_os()
        else:
            raise RuntimeError("Unsupported operating system")

    def __is_mac_os(self):
        return os.uname().sysname == 'Darwin'

    def __get_running_apps_mac_os(self):
        user = subprocess.run("whoami", capture_output=True, text=True).stdout.strip()
        result = subprocess.run(["ps", "-u", user, "-o", "comm"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        apps = [line for line in lines if line.startswith("/Applications/")]
        apps = [app[:app.index(".app/") + 4] for app in apps]
        apps = [app.removeprefix("/Applications/") for app in apps]
        return list(set(apps))
