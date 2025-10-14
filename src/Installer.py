import logging
import shutil

from enum import Enum, auto

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import MissingSchema, ConnectionError, HTTPError

from Settings import Settings
from osutils import app_data, get_os, is_dist
from src.AutorunWithAutorespawn import AutorunWithAutorespawn


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
    def save_settings(server, username, instance_id, instance_name, token, language):
        Settings.create(server, username, instance_id, instance_name, token, language)

    @staticmethod
    def install_autorun_with_autorespawn():
        if is_dist():
            AutorunWithAutorespawn.instance().install()
        else:
            logging.info("installing autorun skipped in non-dist version")

    @staticmethod
    def uninstall(username, password) -> UnregisterInstanceStatus:
        unregister_status = Installer.__unregister_instance(username, password)
        if unregister_status == UnregisterInstanceStatus.OK:
            shutil.rmtree(app_data())
            AutorunWithAutorespawn.instance().uninstall()
        return unregister_status

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
