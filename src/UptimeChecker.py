from datetime import timedelta

from RunningApplications import RunningApplications
from UptimeDb import UsageUpdate
from osutils import is_user_active


class UptimeChecker:
    @staticmethod
    def check_uptime(interval: int) -> UsageUpdate:
        if not is_user_active():
            return UsageUpdate(
                screen_time=timedelta(seconds=0),
                applications={},
                absolute=False
            )
        else:
            apps = RunningApplications.get_running_apps()
            return UsageUpdate(
                screen_time=timedelta(seconds=interval),
                applications={k: timedelta(seconds=interval) for k in apps},
                absolute=False
            )
