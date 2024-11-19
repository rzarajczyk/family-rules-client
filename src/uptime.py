from datetime import timedelta

from RunningApplications import RunningApplications
from UptimeDb import UsageUpdate
from osutils import is_user_active


class Uptime:
    def get(self) -> UsageUpdate:
        pass


class PsUptime(Uptime):
    def __init__(self, interval: int):
        self.interval = interval

    def get(self) -> UsageUpdate:
        if not is_user_active():
            return UsageUpdate(
                screen_time=timedelta(seconds=0),
                applications={},
                absolute=False
            )
        else:
            apps = RunningApplications().get_running_apps()
            return UsageUpdate(
                screen_time=timedelta(seconds=self.interval),
                applications={k: timedelta(seconds=self.interval) for k in apps},
                absolute=False
            )
