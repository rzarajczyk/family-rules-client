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
    def __init__(self, status: RegisterInstanceStatus, token: str = None, message: str = None):
        self.status = status
        self.token = token
        self.message = message


class Installer:

    @staticmethod
    def install(server, username, password, instance_name) -> RegisterInstanceResponse:
        try:
            response = requests.post(
                url=f"{server}/api/register-instance",
                json={
                    'instanceName': instance_name,
                    'os': get_os().name
                },
                auth=HTTPBasicAuth(username, password),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            response_json = response.json()
            status = response_json['status']
            match response_json['status']:
                case 'SUCCESS':
                    return RegisterInstanceResponse(RegisterInstanceStatus.OK, token=response_json['token'])
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
    def save_settings(server, username, instance, token):
        Settings.create(server, username, instance, token)

    @staticmethod
    def install_autorun():
        # if is_dist():
            match get_os():
                case SupportedOs.MAC_OS:
                    Installer.__install_macos_autorun()
                case SupportedOs.WINDOWS:
                    Installer.__install_windows_autorun()
                case _:
                    raise Exception("Unsupported operating system")
        # else:
        #     logging.info("installing autorun skipped in non-dist version")

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
        import win32com.client
        task_name = "FamilyRules Task"
        app_path = path_to_str(dist_path())

        # Get the current user's name
        current_user = os.getlogin()

        # Create Task Scheduler COM object
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()

        # Get the root task folder
        rootFolder = scheduler.GetFolder("\\")

        # Create a new task definition
        task_def = scheduler.NewTask(0)

        # Set general information
        task_def.RegistrationInfo.Description = "Run FamilyRules every 2 minutes"
        task_def.Principal.UserId = current_user
        task_def.Principal.LogonType = 3  # TASK_LOGON_INTERACTIVE_TOKEN

        # Set the trigger (e.g., every 2 minutes)
        trigger = task_def.Triggers.Create(1)  # 1 is for TASK_TRIGGER_TIME

        # Set the StartBoundary to the current time in ISO 8601 format
        current_time = datetime(year=2024, month=1, day=1, hour=0, minute=0, second=0).isoformat()
        trigger.StartBoundary = current_time  # Set the start time to now

        trigger.Repetition.Interval = "PT2M"  # Repetition interval: PT2M means 2 minutes
        trigger.Repetition.Duration = "P10000D"   # Repeat indefinitely, with a maximum duration of 10000 days

        # Set the action (e.g., Start an application)
        action = task_def.Actions.Create(0)  # 0 is for TASK_ACTION_EXEC
        action.Path = app_path

        # Set the settings (e.g., task enabled)
        task_def.Settings.Enabled = True
        task_def.Settings.StopIfGoingOnBatteries = False
        task_def.Settings.DisallowStartIfOnBatteries = False
        task_def.Settings.AllowHardTerminate = False

        # Register the task
        rootFolder.RegisterTaskDefinition(
            task_name,           # Task name
            task_def,            # Task definition
            6,                   # TASK_CREATE_OR_UPDATE
            None,                # User account to run the task
            None,                # Password (None if not required)
            3,                   # TASK_LOGON_INTERACTIVE_TOKEN
            None                 # Security descriptor (None if not needed)
        )

        logging.info(f"Scheduled task '{task_name}' created successfully.")

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
                task_name = "FamilyRules Task"
                result = subprocess.run(['schtasks', '/Delete', '/TN', task_name, '/F'],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    logging.info(f"Task '{task_name}' deleted successfully.")
                else:
                    logging.error(f"Failed to delete task '{task_name}'. Error: {result.stderr}")
            case _:
                pass

    @staticmethod
    def __unregister_instance(username, password) -> UnregisterInstanceStatus:
        settings = Settings.load()
        try:
            response = requests.post(
                url=f"{settings.server}/api/unregister-instance",
                json={'instanceName': settings.instance_name},
                auth=HTTPBasicAuth(username, password),
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
