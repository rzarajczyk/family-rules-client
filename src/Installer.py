import logging
import os
import plistlib
import shutil
import subprocess
from datetime import datetime

from enum import Enum, auto
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import MissingSchema, ConnectionError, HTTPError

from Settings import Settings
from osutils import app_data, path_to_str, dist_path, get_os, SupportedOs, is_dist


class RegisterInstanceStatus(Enum):
    OK = auto()
    HOST_NOT_REACHABLE = auto()
    INVALID_PASSWORD = auto()
    INSTANCE_ALREADY_EXISTS = auto()
    ILLEGAL_INSTANCE_NAME = auto()
    SERVER_ERROR = auto()


class UnregisterInstanceStatus(Enum):
    OK = auto()
    HOST_NOT_REACHABLE = auto()
    INVALID_PASSWORD = auto()
    SERVER_ERROR = auto()


class RegisterInstanceResponse:
    def __init__(self, status: RegisterInstanceStatus, token: str = None, message: str = None, instance_id: str = None):
        self.status = status
        self.token = token
        self.instance_id = instance_id
        self.message = message


class Installer:

    @staticmethod
    def install(server, username, password, instance_name) -> RegisterInstanceResponse:
        try:
            response = requests.post(
                url=f"{server}/api/v2/register-instance",
                json={
                    'instanceName': instance_name,
                    'clientType': get_os().name
                },
                auth=HTTPBasicAuth(username, password),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            response_json = response.json()
            status = response_json['status']
            match response_json['status']:
                case 'SUCCESS':
                    return RegisterInstanceResponse(RegisterInstanceStatus.OK, token=response_json['token'],
                                                    instance_id=response_json['instanceId'])
                case 'INVALID_PASSWORD':
                    return RegisterInstanceResponse(RegisterInstanceStatus.INVALID_PASSWORD)
                case 'INSTANCE_ALREADY_EXISTS':
                    return RegisterInstanceResponse(RegisterInstanceStatus.INSTANCE_ALREADY_EXISTS)
                case 'ILLEGAL_INSTANCE_NAME':
                    return RegisterInstanceResponse(RegisterInstanceStatus.ILLEGAL_INSTANCE_NAME)
                case _:
                    return RegisterInstanceResponse(RegisterInstanceStatus.SERVER_ERROR, message=status)
        except MissingSchema:
            return RegisterInstanceResponse(RegisterInstanceStatus.HOST_NOT_REACHABLE)
        except ConnectionError:
            return RegisterInstanceResponse(RegisterInstanceStatus.HOST_NOT_REACHABLE)
        except HTTPError as e:
            logging.error(f"HTTP Response {e.response.status_code} {e.response.text}")
            return RegisterInstanceResponse(RegisterInstanceStatus.SERVER_ERROR,
                                            message=f"HTTP {e.response.status_code} {e.response.text}")
        except Exception as e:
            logging.error("Could not perform request", e)
            return RegisterInstanceResponse(RegisterInstanceStatus.SERVER_ERROR, message=str(e))

    @staticmethod
    def save_settings(server, username, instance_id, instance_name, token):
        Settings.create(server, username, instance_id, instance_name, token)

    @staticmethod
    def install_autorun():
        if is_dist():
            match get_os():
                case SupportedOs.MAC_OS:
                    Installer.__install_macos_autorun()
                case SupportedOs.WINDOWS:
                    Installer.__install_windows_autorun()
                case _:
                    raise Exception("Unsupported operating system")
        else:
            logging.info("installing autorun skipped in non-dist version")

    @staticmethod
    def __install_macos_autorun():
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

    @staticmethod
    def __install_windows_autorun():
        import datetime
        app_path = str(dist_path().absolute())

        import winreg as reg
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
            reg.SetValueEx(key, "FamilyRules", 0, reg.REG_SZ, f"\"{app_path}\"")
            reg.CloseKey(key)
        except WindowsError as e:
            logging.error(f"Error executing schtasks: {e}")

        near_future = datetime.datetime.now() + datetime.timedelta(minutes=2)
        near_future_time_str = near_future.strftime("%H:%M")
        near_future_date_str = near_future.strftime("%d/%m/%Y")

        Installer.__windows_schtasks([
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

    @staticmethod
    def __windows_schtasks(cmd):
        try:
            import locale
            logging.info("Running schtasks... " + " ".join(cmd))

            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=False)
            system_encoding = locale.getpreferredencoding()

            if result.returncode == 0:
                logging.info(f"Executed schtasks successfully!")
                return True
            else:
                error_output = result.stderr.decode(system_encoding, errors='replace')
                logging.error(f"Error executing schtasks: {error_output}")
                return False

        except Exception as e:
            logging.error(f"Error executing schtasks: {e}")
            return False

    @staticmethod
    def uninstall(username, password) -> UnregisterInstanceStatus:
        unregister_status = Installer.__unregister_instance(username, password)
        if unregister_status == UnregisterInstanceStatus.OK:
            shutil.rmtree(app_data())
            Installer.uninstall_autorun()
        return unregister_status

    @staticmethod
    def uninstall_autorun():
        match get_os():
            case SupportedOs.MAC_OS:
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
            case SupportedOs.WINDOWS:
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
                    return True
                except WindowsError:
                    return False
            case _:
                pass

    @staticmethod
    def __unregister_instance(username, password) -> UnregisterInstanceStatus:
        settings = Settings.load()
        try:
            response = requests.post(
                url=f"{settings.server}/api/v2/unregister-instance",
                auth=HTTPBasicAuth(settings.instance_id, settings.instance_token),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            match response.json()['status']:
                case 'SUCCESS':
                    return UnregisterInstanceStatus.OK
                case 'INVALID_PASSWORD':
                    return UnregisterInstanceStatus.INVALID_PASSWORD
                case _:
                    return UnregisterInstanceStatus.SERVER_ERROR
        except MissingSchema:
            return UnregisterInstanceStatus.HOST_NOT_REACHABLE
        except ConnectionError:
            return UnregisterInstanceStatus.HOST_NOT_REACHABLE
        except HTTPError as e:
            logging.error(f"HTTP Response {e.response.status_code} {e.response.text}")
            return UnregisterInstanceStatus.SERVER_ERROR
        except Exception as e:
            logging.error("Could not perform request", e)
            return UnregisterInstanceStatus.SERVER_ERROR
