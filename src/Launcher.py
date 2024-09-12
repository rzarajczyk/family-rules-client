import logging

import requests
from requests.auth import HTTPBasicAuth

from Settings import Settings


class Launcher:
    def run(self):
        logging.info("Sending launch request")
        settings = Settings.load()
        try:
            server = settings.server
            response = requests.post(
                url=f"{server}/api/v1/launch",
                json={
                    'instanceId': settings.instance_id,
                    'version': "x1",
                    'availableStates': [
                        {
                            "deviceState": "ACTIVE",
                            "title": "Active",
                            "icon": "<path d=\"m424-296 282-282-56-56-226 226-114-114-56 56 170 170Zm56 216q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z\"/>",
                            "description": None
                        },
                        {
                            "deviceState": "LOCKED",
                            "title": "Locked",
                            "icon": "<path d=\"M240-80q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640h40v-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240Zm0-80h480v-400H240v400Zm240-120q33 0 56.5-23.5T560-360q0-33-23.5-56.5T480-440q-33 0-56.5 23.5T400-360q0 33 23.5 56.5T480-280ZM360-640h240v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85v80ZM240-160v-400 400Z\"/>",
                            "description": None
                        },
                        {
                            "deviceState": "LOGGED_OUT",
                            "title": "Logged out",
                            "icon": "<path d=\"M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h280v80H200v560h280v80H200Zm440-160-55-58 102-102H360v-80h327L585-622l55-58 200 200-200 200Z\"/>",
                            "description": None
                        },
                        {
                            "deviceState": "APP_DISABLED",
                            "title": "App disabled",
                            "icon": "<path d=\"m40-120 440-760 440 760H40Zm138-80h604L480-720 178-200Zm302-40q17 0 28.5-11.5T520-280q0-17-11.5-28.5T480-320q-17 0-28.5 11.5T440-280q0 17 11.5 28.5T480-240Zm-40-120h80v-200h-80v200Zm40-100Z\"/>",
                            "description": """
                                The app on the device will be turned off and removed from the "Autorun"/"Autostart".
                                Helpful for updating the app.
                                
                                Remember to manually turn the app on after de-selecting this state.
                            """.strip()
                        }
                    ]
                },
                auth=HTTPBasicAuth(settings.username, settings.instance_token),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
        except Exception as e:
            logging.error("Unable to send launch request", e)