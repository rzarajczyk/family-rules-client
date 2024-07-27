import logging
import os
import shutil
from enum import Enum, auto
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import MissingSchema, ConnectionError, HTTPError

from Settings import Settings
from osutils import is_mac


class ServerLoginStatus(Enum):
    OK = auto()
    HOST_NOT_REACHABLE = auto()
    INVALID_CREDENTIALS = auto()
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
            if response_json['status'] != 'SUCCESS':
                return ServerLoginResponse(ServerLoginStatus.SERVER_ERROR,
                                           token=f"Response status: {response_json['status']}")
            return ServerLoginResponse(ServerLoginStatus.OK, token=response_json['token'])
        except MissingSchema:
            return ServerLoginResponse(ServerLoginStatus.HOST_NOT_REACHABLE, message="Missing URL schema")
        except ConnectionError:
            return ServerLoginResponse(ServerLoginStatus.HOST_NOT_REACHABLE,
                                       message=f"Connection error - host {server} is unreachable")
        except HTTPError as e:
            if e.response.status_code == 403:
                return ServerLoginResponse(ServerLoginStatus.INVALID_CREDENTIALS,
                                           message=f"Invalid username or password")
            else:
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
            agents = os.path.join(Path.home(), "Library", "LaunchAgents")
            file = Path(agents, "pl.zarajczyk.family-rules-client.plist")
            if not file.is_file():
                plist = Path(basedir, "resources", "pl.zarajczyk.family-rules-client.plist")
                shutil.copy(plist, file)
                logging.info(f"plist file installed")
        else:
            raise Exception("Unsupported OS")
