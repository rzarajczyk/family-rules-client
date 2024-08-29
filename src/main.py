import logging
import os
import sys

from Installer import Installer
from Reporter import Reporter
from Settings import Settings
from UptimeDb import AbsoluteUsage
from gui import Gui
from StateController import (StateController)
from osutils import app_data, path_to_str
from basedir import Basedir
from osutils import make_sure_only_one_instance_is_running
from uptime import PsUptime

TICK_INTERVAL_SECONDS = 5
REPORT_INTERVALS_TICK = 2
DEBUG_HTTP_REQUESTS = False

Basedir.init(os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(path_to_str(app_data() / "output.log")),
        logging.StreamHandler(sys.stdout)
    ]
)

if DEBUG_HTTP_REQUESTS:
    import http.client as http_client

    http_client.HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

state_controller = StateController()


def uptime_tick():
    return PsUptime(TICK_INTERVAL_SECONDS).get()


def report_tick(gui: Gui, usage: AbsoluteUsage):
    state = Reporter().submit_report_get_state(usage)
    state_controller.run(state)


if __name__ == "__main__":
    logging.info("App started!")
    make_sure_only_one_instance_is_running()
    gui = Gui(sys.argv)
    state_controller.initialize(gui)

    if not Settings.setup_completed():
        gui.setup_initial_setup_ui()
    else:
        Installer.install_autorun()
        gui.setup_main_ui(
            uptime_tick_interval_ms=TICK_INTERVAL_SECONDS * 1000,
            uptime_tick_function=uptime_tick,
            report_tick_interval_ms=TICK_INTERVAL_SECONDS * REPORT_INTERVALS_TICK * 1000,
            report_tick_function=report_tick
        )
    sys.exit(gui.run())
