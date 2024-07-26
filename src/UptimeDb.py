import datetime
import json
from datetime import timedelta

from src.osutils import app_data


class SingleDayUptimeDb:
    def __init__(self, file):
        with open(file, "r") as f:
            self.file = file
            self.content: dict = json.load(f)

    def get_screen_time(self):
        return timedelta(seconds=self.content.get('screen-time', 0))

    def get_apps(self):
        result = dict()
        for key in self.content.get('applications', {}):
            name = key
            duration = timedelta(seconds=self.content.get('applications', {}).get(key, 0))
            result[name] = duration
        return result

    def inc_screen_time(self, amount):
        self.content['screen-time'] = self.content.get('screen-time', 0) + amount

    def inc_apps(self, apps, amount):
        if 'applications' not in self.content:
            self.content['applications'] = dict()
        for app in apps:
            self.content['applications'][app] = self.content['applications'].get(app, 0) + amount

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.content, f, indent=4)


class UptimeDb:
    def update(self, apps: list[str], tick_seconds: int):
        file = self.get_file_for_today()
        db = SingleDayUptimeDb(file)

        db.inc_screen_time(tick_seconds)
        db.inc_apps(apps, tick_seconds)
        db.save()
        return Usage(db.get_screen_time(), db.get_apps())

    def get(self):
        db = SingleDayUptimeDb(self.get_file_for_today())
        return Usage(db.get_screen_time(), db.get_apps())

    def get_file_for_today(self):
        data_dir = app_data() / "data"
        data_dir.mkdir(exist_ok=True)

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = data_dir / today
        if not file_path.exists():
            with open(file_path, "w") as f:
                f.write("{}")
        return file_path


class Usage:
    def __init__(self, screen_time, applications):
        self.screen_time: timedelta = screen_time
        self.applications: dict[str, timedelta] = applications
