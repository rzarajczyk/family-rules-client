from pathlib import Path

from pathutils import path_to_str
from osutils import get_os, dist_path, app_data

import logging

from osutils import OperatingSystem


class AutorunWithAutorespawn:
    def install(self):
        pass
    def uninstall(self):
        pass
    @staticmethod
    def instance():
        match get_os():
            case OperatingSystem.MAC_OS:
                return MacOSAutorunWithAutorespawn()
            case OperatingSystem.WINDOWS:
                return WindowsAutorunWithAutorespawn()
            case _ as os:
                raise Exception(f"Unsupported OS: {os}")

class MacOSAutorunWithAutorespawn(AutorunWithAutorespawn):
    def install(self):
        import plistlib
        import subprocess
        path = path_to_str(dist_path() / "Contents" / "MacOS" / "FamilyRules")
        expected_plist_content = {
            "Label": "pl.zarajczyk.family-rules-client",
            "ProgramArguments": [path],
            "RunAtLoad": True,
            "KeepAlive": True,
            "StandardErrorPath": path_to_str(app_data() / "family-rules-client-stderr.log"),
            "StandardOutPath": path_to_str(app_data() / "family-rules-client-stdout.log"),
        }
        launch_agent = Path.home() / "Library" / "LaunchAgents" / "pl.zarajczyk.family-rules-client.plist"

        existing_plist_contents = {}
        if launch_agent.is_file():
            with launch_agent.open("rb") as f:
                existing_plist_contents = plistlib.load(f)

        if existing_plist_contents != expected_plist_content:
            logging.info(f"Installing LaunchAgent {path}")
            with launch_agent.open("wb") as f:
                plistlib.dump(expected_plist_content, f)
            process = subprocess.Popen(
                ["launchctl", "load", launch_agent],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            stdout = process.communicate()
            if process.returncode != 0 or not stdout:
                logging.error(f"'launchctl load' exited with code {process.returncode}, output: {stdout}")

    def uninstall(self):
        import subprocess
        import os
        path = Path.home() / "Library" / "LaunchAgents" / "pl.zarajczyk.family-rules-client.plist"
        process = subprocess.Popen(
            ["launchctl", "unload", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        stdout = process.communicate()
        os.remove(path)
        if process.returncode != 0 or not stdout:
            logging.error(
                f"'launchctl unload' exited with code {process.returncode}, output: {stdout}")

class WindowsAutorunWithAutorespawn(AutorunWithAutorespawn):
    def install(self):
        import datetime
        import os

        app_path = str(dist_path().absolute())

        self._install_registry_run(app_path)

        near_future = datetime.datetime.now() + datetime.timedelta(minutes=2)
        near_future_time_str = near_future.strftime("%H:%M")
        near_future_date_str = near_future.strftime("%d/%m/%Y")

        self.__windows_schtasks([
            "schtasks",
            "/create",
            "/tn", f"FamilyRules_{os.getenv('USERNAME')}",
            "/tr", f'"{app_path}"',
            "/sc", "MINUTE",
            "/mo", "1",
            "/st", near_future_time_str,
            "/sd", near_future_date_str,
            "/rl", "LIMITED",
            "/f"
        ])

    def _install_registry_run(self, app_path):
        import winreg as reg
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
            reg.SetValueEx(key, "FamilyRules", 0, reg.REG_SZ, f"\"{app_path}\"")
            reg.CloseKey(key)
        except WindowsError as e:
            logging.error("Unable to set registry value for FamilyRules", e)


    def __windows_schtasks(self, cmd):
        import subprocess
        try:
            import locale
            logging.info("Installing scheduled task... " + " ".join(cmd))

            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=False)
            system_encoding = locale.getpreferredencoding()

            if result.returncode == 0:
                logging.info(f"Executed schtasks successfully!")
            else:
                error_output = result.stderr.decode(system_encoding, errors='replace')
                logging.error(f"Error executing schtasks: {error_output}")
        except Exception as e:
            logging.error(f"Error executing schtasks: {e}")


    def uninstall(self):
        import subprocess
        import os
        task_name = f"FamilyRules_{os.getenv('USERNAME')}"
        result = subprocess.run(['schtasks', '/Delete', '/TN', task_name, '/F'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logging.info(f"Task '{task_name}' deleted successfully.")
        else:
            logging.error(f"Failed to delete task '{task_name}'. Error: {result.stderr}")

        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

        import winreg as reg

        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
            reg.DeleteValue(key, "FamilyRules")
            reg.CloseKey(key)
        except WindowsError as e:
            logging.error("Unable to remove registry value for FamilyRules", e)