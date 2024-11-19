import json
import logging
import re
from base64 import b64encode

import requests
from requests.auth import to_native_string, HTTPBasicAuth
from websockets import ConnectionClosed
from websockets.sync.client import connect

from Settings import Settings
from StateController import State
from UptimeDb import AbsoluteUsage


class Reporter:
    def __init__(self):
        # self.internal = ReporterRest()
        self.internal = ReporterWs()

    def submit_report_get_state(self, usage: AbsoluteUsage) -> State:
        return self.internal.submit_report_get_state(usage)


class ReporterRest:
    def submit_report_get_state(self, usage: AbsoluteUsage) -> State:
        settings = Settings.load()
        try:
            server = settings.server
            response = requests.post(
                url=f"{server}/api/v1/report",
                json={
                    'instanceId': settings.instance_id,
                    'screenTime': usage.screen_time.total_seconds(),
                    'applications': {k: v.total_seconds() for k, v in usage.applications.items()}
                },
                auth=HTTPBasicAuth(settings.username, settings.instance_token),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            response_json = response.json()
            return State(response_json)
        except Exception as e:
            logging.error("Unable to submit report", e)
            return State.empty()


class ReporterWs:
    def __init__(self):
        self.websocket = None
        self.uri = None
        self.settings = Settings.load()  # load settings in the constructor for easy access later
        self.uri = f"ws://{re.sub(r'^https?://', '', self.settings.server)}/api/v1/streaming-report"
        self.headers = {
            "Authorization": _basic_auth_str(self.settings.username, self.settings.instance_token)
        }

    def _connect(self):
        self.websocket = connect(self.uri, additional_headers=self.headers)
        logging.info("WebSocket connection established")

    def _send_and_receive_single_attempt(self, usage: AbsoluteUsage):
        report_request = {
            "instanceId": self.settings.instance_id,
            "screenTime": usage.screen_time.total_seconds(),
            "applications": {k: v.total_seconds() for k, v in usage.applications.items()}
        }
        self.websocket.send(json.dumps(report_request))

        response = self.websocket.recv()
        response_json = json.loads(response)
        return State(response_json)

    def _send_and_receive_with_retry(self, usage: AbsoluteUsage):
        try:
            return self._send_and_receive_single_attempt(usage)
        except ConnectionClosed as e:
            logging.error(f"WebSocket connection closed: {e}; Reconnecting...")
            self._connect()
            return self._send_and_receive_single_attempt(usage)

    def submit_report_get_state(self, usage: AbsoluteUsage) -> State:
        try:
            if self.websocket is None:
                self._connect()
            return self._send_and_receive_with_retry(usage)
        except Exception as e:
            logging.error(f"Exception during websocket communication: {e}")
            return State.empty()  # Failed to connect


def _basic_auth_str(username, password):  # helper function to create Basic Authorization header
    """Returns a Basic Auth string."""

    if isinstance(username, str):
        username = username.encode("latin1")

    if isinstance(password, str):
        password = password.encode("latin1")

    authstr = "Basic " + to_native_string(
        b64encode(b":".join((username, password))).strip()
    )

    return authstr
