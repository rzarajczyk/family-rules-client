import datetime
import sqlite3
from datetime import timedelta
from os.path import expanduser

from RunningApplications import RunningApplications
from UptimeDb import UsageUpdate


class Uptime:
    def get(self) -> UsageUpdate:
        pass


class PsUptime(Uptime):
    def __init__(self, interval: int):
        self.interval = interval

    def get(self) -> UsageUpdate:
        apps = RunningApplications().get_running_apps()
        return UsageUpdate(
            screen_time=timedelta(seconds=self.interval),
            applications={k: timedelta(seconds=self.interval) for k in apps},
            absolute=False
        )


class AppleScreenTimeUptime(Uptime):
    # https://felixkohlhas.com/projects/screentime/
    def get(self) -> UsageUpdate:
        usage = self.__query_database(datetime.date.today())
        sum = self.__sum_usage_seconds_per_app(usage)
        sum = dict(reversed(sorted(sum.items(), key=lambda x: x[1])))
        applications = {}
        for app in sum:
            duration = datetime.timedelta(seconds=sum[app])
            name = app
            applications[name] = duration
        return UsageUpdate(
            screen_time=timedelta(seconds=0),
            applications=applications,
            absolute=True
        )

    def __date_to_unix_timestamp_utc(self, date_obj):
        # Convert the date object to a datetime object
        dt = datetime.datetime.combine(date_obj, datetime.datetime.min.time())

        # Make the datetime object timezone-aware (UTC)
        dt = dt.replace(tzinfo=datetime.timezone.utc)

        # Convert the datetime object to a Unix timestamp
        unix_timestamp = int(dt.timestamp())

        return unix_timestamp

    def __from_utc_timestamp(self, t):
        return datetime.datetime.fromtimestamp(t, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')

    def __query_database(self, date: datetime.date):
        # Connect to the SQLite database
        knowledge_db = expanduser("~/Library/Application Support/Knowledge/knowledgeC.db")
        with sqlite3.connect(knowledge_db) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()

            # Execute the SQL query to fetch data
            # Modified from https://rud.is/b/2019/10/28/spelunking-macos-screentime-app-usage-with-r/
            date_from = self.__date_to_unix_timestamp_utc(date)
            date_to = self.__date_to_unix_timestamp_utc(date + datetime.timedelta(days=1))
            query = f"""
            SELECT
                ZOBJECT.ZVALUESTRING AS "app", 
                (ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) AS "usage_seconds",
                (ZOBJECT.ZSTARTDATE + 978307200) as "start_time", 
                (ZOBJECT.ZENDDATE + 978307200) as "end_time",
                (ZOBJECT.ZCREATIONDATE + 978307200) as "created_at", 
                ZOBJECT.ZSECONDSFROMGMT AS "tz",
                ZSOURCE.ZDEVICEID AS "device_id",
                ZMODEL AS "device_model"
            FROM
                ZOBJECT 
                LEFT JOIN
                ZSTRUCTUREDMETADATA 
                ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK 
                LEFT JOIN
                ZSOURCE 
                ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK 
                LEFT JOIN
                ZSYNCPEER
                ON ZSOURCE.ZDEVICEID = ZSYNCPEER.ZDEVICEID
            WHERE
                ZSTREAMNAME = "/app/usage"
                AND
                start_time > {date_from}
                AND
                end_time < {date_to}
            ORDER BY
                ZSTARTDATE DESC
            """
            cur.execute(query)

            # Fetch all rows from the result set
            rows = cur.fetchall()
            results = [dict(row) for row in rows]
            for result in results:
                result['start_time'] = self.__from_utc_timestamp(result['start_time'])
                result['end_time'] = self.__from_utc_timestamp(result['end_time'])
                result['created_at'] = self.__from_utc_timestamp(result['created_at'])
            return results

    def __sum_usage_seconds_per_app(self, data):
        usage_dict = {}
        for entry in data:
            app = entry['app']
            usage_seconds = entry['usage_seconds']
            if app in usage_dict:
                usage_dict[app] += usage_seconds
            else:
                usage_dict[app] = usage_seconds
        return usage_dict
