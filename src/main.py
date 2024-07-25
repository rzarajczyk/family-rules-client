import logging
import os
import sys

from Reporter import Reporter
from RunningApplications import RunningApplications
from UptimeDb import UptimeDb
from gui import Gui

TICK_INTERVAL_SECONDS = 5

logging.basicConfig(filename="/Users/rafal/output.log", level=logging.INFO)

BASEDIR = os.path.dirname(__file__)


def tick(gui: Gui):
    apps = RunningApplications().get_running_apps()
    logging.info(apps)
    usage = UptimeDb().update(apps, TICK_INTERVAL_SECONDS)

    gui.main_window.update_screen_time(usage.screen_time)
    gui.main_window.update_applications_usage(usage.applications)

    logging.info(usage)
    action = Reporter().submit_report_get_action(usage)
    logging.info(action)
    action.execute(gui)


if __name__ == "__main__":
    logging.warning("running")
    Gui(BASEDIR).run(
        tick_interval_ms=TICK_INTERVAL_SECONDS * 1000,
        tick_function=tick,
        argv=sys.argv
    )
