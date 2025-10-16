import logging
import time
from base64 import b64encode
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

from Settings import Settings
from osutils import app_version
from AppDb import AppDb


class Launcher:
    @staticmethod
    def run():
        logging.info("Sending launch request")
        settings = Settings.load()
        try:
            server = settings.server
            
            # Get all known apps from AppDb and format them for the API
            app_db = AppDb()
            known_apps = {}
            
            for app in app_db:
                # Convert icon to base64 if it exists
                icon_base64 = None
                if app.icon_path and Path(app.icon_path).exists():
                    try:
                        with open(app.icon_path, "rb") as icon_file:
                            icon_data = icon_file.read()
                            icon_base64 = b64encode(icon_data).decode('utf-8')
                    except Exception:
                        # If we can't read the icon, just skip it
                        icon_base64 = None
                
                known_apps[app.app_path] = {
                    "app_name": app.app_name,
                    "icon_base64_png": icon_base64
                }
            
            response = requests.post(
                url=f"{server}/api/v2/launch",
                json={
                    'version': app_version(),
                    'knownApps': known_apps,
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
                            "deviceState": "LOCKED_WITH_COUNTDOWN",
                            "title": "Locked (with 60s countdown)",
                            "icon": "<path d=\"M263.72-96Q234-96 213-117.15T192-168v-384q0-29.7 21.15-50.85Q234.3-624 264-624h24v-96q0-79.68 56.23-135.84 56.22-56.16 136-56.16Q560-912 616-855.84q56 56.16 56 135.84v96h24q29.7 0 50.85 21.15Q768-581.7 768-552v384q0 29.7-21.16 50.85Q725.68-96 695.96-96H263.72Zm.28-72h432v-384H264v384Zm216.21-120Q510-288 531-309.21t21-51Q552-390 530.79-411t-51-21Q450-432 429-410.79t-21 51Q408-330 429.21-309t51 21ZM360-624h240v-96q0-50-35-85t-85-35q-50 0-85 35t-35 85v96Zm-96 456v-384 384Z\" id=\"path1\" /><circle style=\"fill:#fdffff;fill-opacity:1;stroke-width:48\" id=\"path2\" cx=\"732.20337\" cy=\"-219.66103\" r=\"215.59323\" /><path d=\"m 731.79661,-111.45763 q 44.23729,0 75.20339,-30.9661 30.9661,-30.9661 30.9661,-75.20339 0,-44.2373 -30.9661,-75.20342 -30.9661,-30.96603 -75.20339,-30.96603 v 106.16945 l -75.20338,75.20339 q 15.48305,14.5983 34.72626,22.78221 19.24322,8.18389 40.47712,8.18389 z m 0,70.77966 q -36.71695,0 -69.01017,-13.934738 -32.29321,-13.934749 -56.18135,-37.822879 -23.88814,-23.888143 -37.82288,-56.181363 -13.93475,-32.29322 -13.93475,-69.01017 0,-36.71692 13.93475,-69.01013 13.93474,-32.29329 37.82288,-56.18136 23.88814,-23.88815 56.18135,-37.8229 32.29322,-13.93476 69.01017,-13.93476 36.71695,0 69.01017,13.93476 32.29322,13.93475 56.18136,37.8229 23.88813,23.88807 37.82288,56.18136 13.93474,32.29321 13.93474,69.01013 0,36.71695 -13.93474,69.01017 -13.93475,32.29322 -37.82288,56.181363 -23.88814,23.88813 -56.18136,37.822879 -32.29322,13.934738 -69.01017,13.934738 z m 0,-35.389827 q 59.27797,0 100.41865,-41.140673 41.14068,-41.14068 41.14068,-100.41865 0,-59.27798 -41.14068,-100.41866 -41.14068,-41.14068 -100.41865,-41.14068 -59.27797,0 -100.41864,41.14068 -41.14068,41.14068 -41.14068,100.41866 0,59.27797 41.14068,100.41865 41.14067,41.140673 100.41864,41.140673 z m 0,-141.559323 z\" id=\"path1-2\" style=\"stroke-width:0.442373\" />",
                            "description": None
                        },
                        {
                            "deviceState": "LOGGED_OUT",
                            "title": "Logged out",
                            "icon": "<path d=\"M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h280v80H200v560h280v80H200Zm440-160-55-58 102-102H360v-80h327L585-622l55-58 200 200-200 200Z\"/>",
                            "description": None
                        },
                        {
                            "deviceState": "LOGGED_OUT_WITH_COUNTDOWN",
                            "title": "Logged out (with 60s countdown)",
                            "icon": "<path d=\"M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h280v80H200v560h280v80H200Zm440-160-55-58 102-102H360v-80h327L585-622l55-58 200 200-200 200Z\" id=\"path1\" /><circle style=\"fill:#fdffff;fill-opacity:1;stroke-width:40\" id=\"path2\" cx=\"761.35583\" cy=\"-200.00003\" r=\"179.661\" /><path d=\"m 761.01693,-109.83054 q 36.8644,0 62.66948,-25.80508 25.80508,-25.80508 25.80508,-62.66948 0,-36.86442 -25.80508,-62.66951 -25.80508,-25.80502 -62.66948,-25.80502 v 88.47453 l -62.66947,62.66948 q 12.90254,12.16525 28.93854,18.98517 16.03602,6.81991 33.73093,6.81991 z m 0,58.983043 q -30.59745,0 -57.50847,-11.61228 -26.911,-11.61229 -46.81778,-31.51906 -19.90678,-19.906793 -31.51906,-46.817803 -11.61229,-26.91101 -11.61229,-57.50846 0,-30.59743 11.61229,-57.50844 11.61228,-26.91107 31.51906,-46.81779 19.90678,-19.90679 46.81778,-31.51908 26.91102,-11.6123 57.50847,-11.6123 30.59745,0 57.50847,11.6123 26.91101,11.61229 46.81779,31.51908 19.90677,19.90672 31.51906,46.81779 11.61228,26.91101 11.61228,57.50844 0,30.59745 -11.61228,57.50846 -11.61229,26.91101 -31.51906,46.817803 -19.90678,19.90677 -46.81779,31.51906 -26.91102,11.61228 -57.50847,11.61228 z m 0,-29.49152 q 49.3983,0 83.6822,-34.283893 34.28389,-34.28389 34.28389,-83.68219 0,-49.39831 -34.28389,-83.68221 -34.2839,-34.28389 -83.6822,-34.28389 -49.3983,0 -83.68219,34.28389 -34.28389,34.2839 -34.28389,83.68221 0,49.3983 34.28389,83.68219 34.28389,34.283893 83.68219,34.283893 z m 0,-117.966083 z\" id=\"path1-2\" style=\"stroke-width:0.368644\" />",
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
                    ],
                    'timezoneOffsetSeconds': time.timezone
                },
                auth=HTTPBasicAuth(settings.instance_id, settings.instance_token),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
        except Exception as e:
            logging.error("Unable to send launch request", e)