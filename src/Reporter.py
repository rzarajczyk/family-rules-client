import logging

import requests
from requests.auth import HTTPBasicAuth

from Settings import Settings
from UptimeDb import AbsoluteUsage
from actions import *


class Reporter:
    def submit_report_get_action(self, usage: AbsoluteUsage):
        settings = Settings.load()
        try:
            server = settings.server
            response = requests.post(
                url=f"{server}/report",
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
            action_type = response_json['action']['type']

            if action_type == 'NO_ACTION':
                return NoAction()
            elif action_type == 'LOCK_SYSTEM':
                return LockSystem()
            else:
                return NoAction()
        except Exception as e:
            logging.error("Unable to submit report", e)
            return NoAction()
