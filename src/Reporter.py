import logging
from base64 import b64encode

import requests
from requests.auth import to_native_string, HTTPBasicAuth

from Settings import Settings
from StateController import State
from UptimeDb import AbsoluteUsage


class Reporter:
    def __init__(self):
        self.internal = ReporterRest()
        # self.internal = ReporterWs()

    def submit_report_get_state(self, usage: AbsoluteUsage) -> State:
        return self.internal.submit_report_get_state(usage)


class ReporterRest:
    def submit_report_get_state(self, usage: AbsoluteUsage) -> State:
        settings = Settings.load()
        try:
            server = settings.server
            response = requests.post(
                url=f"{server}/api/v2/report",
                json={
                    'screenTime': usage.screen_time.total_seconds(),
                    'applications': {k: v.total_seconds() for k, v in usage.applications.items()}
                },
                auth=HTTPBasicAuth(settings.instance_id, settings.instance_token),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            response_json = response.json()
            return State(response_json)
        except Exception as e:
            logging.error("Unable to submit report", e)
            return State.empty()

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
