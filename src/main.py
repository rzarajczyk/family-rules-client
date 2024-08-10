import logging
import os
import sys

from Reporter import Reporter
from RunningApplications import RunningApplications
from Settings import Settings
from UptimeDb import UptimeDb, AbsoluteUsage
from gui import Gui
from osutils import app_data, path_to_str
from Installer import Installer
from uptime import PsUptime

TICK_INTERVAL_SECONDS = 5
REPORT_INTERVALS_TICK = 6
DEBUG_HTTP_REQUESTS = True

logging.basicConfig(filename=path_to_str(app_data() / "output.log"),
                    level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

if DEBUG_HTTP_REQUESTS:
    import http.client as http_client

    http_client.HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

BASEDIR = os.path.dirname(__file__)


def uptime_tick():
    settings = Settings.load()
    return PsUptime(TICK_INTERVAL_SECONDS).get()


def report_tick(gui: Gui, usage: AbsoluteUsage):
    action = Reporter().submit_report_get_action(usage)
    action.execute(gui)


if __name__ == "__main__":
    logging.info("App started!")
    gui = Gui(BASEDIR, sys.argv)

    if not Settings.setup_completed():
        gui.setup_initial_setup_ui()
    else:
        Installer.install_autorun(BASEDIR)
        gui.setup_main_ui(
            uptime_tick_interval_ms=TICK_INTERVAL_SECONDS * 1000,
            uptime_tick_function=uptime_tick,
            report_tick_interval_ms=TICK_INTERVAL_SECONDS * REPORT_INTERVALS_TICK * 1000,
            report_tick_function=report_tick
        )
    sys.exit(gui.run())
