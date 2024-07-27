import logging
import os
import sys

from Reporter import Reporter
from RunningApplications import RunningApplications
from UptimeDb import UptimeDb
from gui import Gui
from osutils import app_data
from src.Settings import Settings

TICK_INTERVAL_SECONDS = 5
DEBUG_HTTP_REQUESTS = False

logging.basicConfig(filename=app_data().absolute().as_posix() + "/output.log",
                    level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

if DEBUG_HTTP_REQUESTS:
    import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

BASEDIR = os.path.dirname(__file__)


def tick(gui: Gui):
    apps = RunningApplications().get_running_apps()
    usage = UptimeDb().update(apps, TICK_INTERVAL_SECONDS)

    gui.main_window.update_screen_time(usage.screen_time)
    gui.main_window.update_applications_usage(usage.applications)

    action = Reporter().submit_report_get_action(usage)
    action.execute(gui)


if __name__ == "__main__":
    logging.info("App started!")
    # check_install(BASEDIR)
    gui = Gui(BASEDIR, sys.argv)

    if not Settings.setup_completed():
        gui.setup_initial_setup_ui()
    else:
        gui.setup_main_ui(
            tick_interval_ms=TICK_INTERVAL_SECONDS * 1000,
            tick_function=tick
        )
    sys.exit(gui.run())
