import logging
import os
import sys

from Installer import Installer
from Reporter import Reporter
from Settings import Settings
from StateController import (StateController)
from UptimeDb import AbsoluteUsage
from Basedir import Basedir
from global_exception_handler import global_exception_handler
from gui import Gui
from osutils import app_data
from pathutils import path_to_str
from osutils import make_sure_only_one_instance_is_running, is_dist
from translations import initialize_translations
from UptimeChecker import UptimeChecker

TICK_INTERVAL_SECONDS = 5
REPORT_INTERVALS_TICK = 4
DEBUG_HTTP_REQUESTS = False

Basedir.init(os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(path_to_str(app_data() / "output.log"))] +
             ([logging.StreamHandler(sys.stdout)] if not is_dist() else [])
)

if DEBUG_HTTP_REQUESTS:
    import http.client as http_client

    http_client.HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

state_controller = StateController()
reporter = Reporter()


def uptime_tick():
    return UptimeChecker.check_uptime(TICK_INTERVAL_SECONDS)


def report_tick(gui: Gui, usage: AbsoluteUsage, first_run: bool):
    state = reporter.submit_report_get_state(usage)
    state_controller.run(state, first_run)


if __name__ == "__main__":
    sys.excepthook = global_exception_handler

    logging.info("App starting!")
    make_sure_only_one_instance_is_running()

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    initialize_translations()

    gui = Gui(sys.argv)
    state_controller.initialize(gui)

    if not Settings.setup_completed():
        gui.setup_initial_setup_ui()
    else:
        Installer.install_autorun_with_autorespawn()
        gui.setup_main_ui(
            uptime_tick_interval_ms=TICK_INTERVAL_SECONDS * 1000,
            uptime_tick_function=uptime_tick,
            report_tick_interval_ms=TICK_INTERVAL_SECONDS * REPORT_INTERVALS_TICK * 1000,
            report_tick_function=report_tick
        )
    sys.exit(gui.run())
