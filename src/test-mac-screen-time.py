import datetime
import os
import plistlib
import sqlite3
import subprocess
from os.path import expanduser


###
# https://felixkohlhas.com/projects/screentime/
###


def from_utc_timestamp(t):
    return datetime.datetime.fromtimestamp(t, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')


def get_app_name_1(bundle_identifier):
    # Use mdfind to locate the application
    try:
        result = subprocess.run(['mdfind', f'kMDItemCFBundleIdentifier == "{bundle_identifier}"'], capture_output=True,
                                text=True)
        app_paths = result.stdout.strip().split("\n")

        if not app_paths or app_paths[0] == '':
            return f"No application found for bundle identifier: {bundle_identifier}"

        # Assuming the first result is the correct one
        app_path = app_paths[0]
        info_plist_path = os.path.join(app_path, 'Contents', 'Info.plist')

        # Read Info.plist
        with open(info_plist_path, 'rb') as f:
            plist = plistlib.load(f)
            app_name = plist.get('CFBundleDisplayName') or plist.get('CFBundleName')
            return app_name if app_name else f"Name not found in Info.plist for {bundle_identifier}"

    except Exception as e:
        return bundle_identifier


def get_app_name_2(bundle_identifier):
    # Use mdfind to locate the application
    try:
        result = subprocess.run(['mdfind', f'kMDItemCFBundleIdentifier == "{bundle_identifier}"'], capture_output=True, text=True)
        app_paths = result.stdout.strip().split("\n")

        if not app_paths or app_paths[0] == '':
            return f"No application found for bundle identifier: {bundle_identifier}"

        # Assuming the first result is the correct one
        app_path = app_paths[0]
        info_plist_path = os.path.join(app_path, 'Contents', 'Info.plist')

        # Read Info.plist
        with open(info_plist_path, 'rb') as f:
            plist = plistlib.load(f)
            app_name = plist.get('CFBundleDisplayName') or plist.get('CFBundleName')
            if not app_name:
                app_name = plist.get('CFBundleExecutable')  # Fallback to executable name
            return app_name if app_name else f"Name not found in Info.plist for {bundle_identifier}"

    except Exception as e:
        return bundle_identifier


def date_to_unix_timestamp_utc(date_obj):
    # Convert the date object to a datetime object
    dt = datetime.datetime.combine(date_obj, datetime.datetime.min.time())

    # Make the datetime object timezone-aware (UTC)
    dt = dt.replace(tzinfo=datetime.timezone.utc)

    # Convert the datetime object to a Unix timestamp
    unix_timestamp = int(dt.timestamp())

    return unix_timestamp


def query_database(date: datetime.date):
    # Connect to the SQLite database
    knowledge_db = expanduser("~/Library/Application Support/Knowledge/knowledgeC.db")
    with sqlite3.connect(knowledge_db) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        # Execute the SQL query to fetch data
        # Modified from https://rud.is/b/2019/10/28/spelunking-macos-screentime-app-usage-with-r/
        date_from = date_to_unix_timestamp_utc(date)
        date_to = date_to_unix_timestamp_utc(date + datetime.timedelta(days=1))
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
            result['start_time'] = from_utc_timestamp(result['start_time'])
            result['end_time'] = from_utc_timestamp(result['end_time'])
            result['created_at'] = from_utc_timestamp(result['created_at'])
        return results


def sum_usage_seconds_per_app(data):
    usage_dict = {}
    for entry in data:
        app = entry['app']
        usage_seconds = entry['usage_seconds']
        if app in usage_dict:
            usage_dict[app] += usage_seconds
        else:
            usage_dict[app] = usage_seconds
    return usage_dict


usage = query_database(datetime.date.today())
sum = sum_usage_seconds_per_app(usage)
sum = dict(reversed(sorted(sum.items(), key=lambda x: x[1])))

for app in sum:
    duration = datetime.timedelta(seconds=sum[app])
    name = get_app_name_2(app)
    print(f"{name} - {duration}")
