import subprocess

from osutils import is_mac


class RunningApplicationsFetcher:
    def get_running_apps(self):
        if is_mac():
            return self.__get_running_apps_mac_os()
        else:
            raise Exception("Unsupported operating system")

    def __get_running_apps_mac_os(self):
        user = subprocess.run("whoami", capture_output=True, text=True).stdout.strip()
        result = subprocess.run(["ps", "-u", user, "-o", "comm"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        apps = [line for line in lines if line.startswith("/Applications/")]
        apps = [app[:app.index(".app/") + 4] for app in apps]
        apps = [app.removeprefix("/Applications/") for app in apps]
        return list(set(apps))
