import logging

import requests
from requests.auth import HTTPBasicAuth

from Settings import Settings
from StateController import *
from UptimeDb import AbsoluteUsage


class Reporter:
    def submit_report_get_state(self, usage: AbsoluteUsage) -> State:
        settings = Settings.load()
        try:
            server = settings.server
            response = requests.post(
                url=f"{server}/api/report",
                json={
                    'instanceName': settings.instance_name,
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
            return None
