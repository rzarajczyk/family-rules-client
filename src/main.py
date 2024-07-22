import datetime
import sys

from apscheduler.schedulers.background import BackgroundScheduler

from Reporter import Reporter
from RunningApplicationsFetcher import RunningApplicationsFetcher
from UptimeDb import UptimeDb
from gui import Gui

TICK_INTERVAL_SECONDS = 5

gui = Gui()
gui.setup()


def tick():
    apps = RunningApplicationsFetcher().get_running_apps()
    print(apps)
    usage = UptimeDb().update(apps, TICK_INTERVAL_SECONDS)
    print(usage)
    action = Reporter().submit_report_get_action(usage)
    print(action)
    action.execute(gui)


s = BackgroundScheduler()
s.add_job(tick, trigger='interval', seconds=TICK_INTERVAL_SECONDS, next_run_time=datetime.datetime.now())
s.start()

sys.exit(gui.run())
