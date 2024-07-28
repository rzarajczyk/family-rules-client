import logging
import os
import shutil
from enum import Enum, auto
from pathlib import Path
import plistlib

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import MissingSchema, ConnectionError, HTTPError

from Settings import Settings
from osutils import is_mac, app_data, path_to_str, dist_path


class ServerLoginStatus(Enum):
    OK = auto()
    HOST_NOT_REACHABLE = auto()
    INVALID_PASSWORD = auto()
    INSTANCE_ALREADY_EXISTS = auto()
    ILLEGAL_INSTANCE_NAME = auto()
    SERVER_ERROR = auto()


class ServerLoginResponse:
    def __init__(self, status: ServerLoginStatus, token: str = None, message: str = None):
        self.status = status
        self.token = token
        self.message = message


class Installer:

    @staticmethod
    def do_server_login(server, username, password, instance_name) -> ServerLoginResponse:
        try:
            response = requests.post(
                url=f"{server}/setup",
                json={'instanceName': instance_name},
                auth=HTTPBasicAuth(username, password),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            response_json = response.json()
            status = response_json['status']
            if status == 'SUCCESS':
                return ServerLoginResponse(ServerLoginStatus.OK, token=response_json['token'])
            elif status == 'INVALID_PASSWORD':
                return ServerLoginResponse(ServerLoginStatus.INVALID_PASSWORD, message=f"Invalid username or password")
            elif status == 'INSTANCE_ALREADY_EXISTS':
                return ServerLoginResponse(ServerLoginStatus.INSTANCE_ALREADY_EXISTS,
                                           message=f"Instance already exists")
            elif status == 'ILLEGAL_INSTANCE_NAME':
                return ServerLoginResponse(ServerLoginStatus.ILLEGAL_INSTANCE_NAME,
                                           message=f"Incorrect instance name (probably too short)")
            else:
                return ServerLoginResponse(ServerLoginStatus.SERVER_ERROR,
                                           token=f"Unknown server response: {response_json['status']}")
        except MissingSchema:
            return ServerLoginResponse(ServerLoginStatus.HOST_NOT_REACHABLE, message="Missing URL schema")
        except ConnectionError:
            return ServerLoginResponse(ServerLoginStatus.HOST_NOT_REACHABLE,
                                       message=f"Connection error - host {server} is unreachable")
        except HTTPError as e:
            return ServerLoginResponse(ServerLoginStatus.SERVER_ERROR,
                                       message=f"Server returned HTTP {e.response.status_code} {e.response.text}")
        except Exception as e:
            logging.error("Could not perform request", e)
            return ServerLoginResponse(ServerLoginStatus.SERVER_ERROR, message=str(e))

    @staticmethod
    def save_settings(server, username, instance, token):
        Settings.create(server, username, instance, token)

    @staticmethod
    def install_autorun(basedir):
        if is_mac():
            plist_content = {
                "Label": "pl.zarajczyk.family-rules-client",
                "ProgramArguments": [path_to_str(dist_path(basedir))],
                "RunAtLoad": True,
                "KeepAlive": True,
                "StandardErrorPath": path_to_str(app_data() / "family-rules-client-stderr.log"),
                "StandardOutPath": path_to_str(app_data() / "family-rules-client-stdout.log"),
            }
            launch_agent = Path.home() / "Library" / "LaunchAgents" / "pl.zarajczyk.family-rules-client.plist"
            if not launch_agent.is_file():
                with launch_agent.open("wb") as f:
                    plistlib.dump(plist_content, f)
        else:
            raise Exception("Unsupported OS")
