import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from Reporter import Reporter
from RunningApplicationsFetcher import RunningApplicationsFetcher
from UptimeDb import UptimeDb

FETCH_INTERVAL = 5


def run():
    # print(threading.current_thread().name)
    apps = RunningApplicationsFetcher().get_running_apps()
    print(apps)
    usage = UptimeDb().update(apps, FETCH_INTERVAL)
    print(usage)
    action = Reporter().report(usage)
    print(action)
    action.execute()


# if __name__ == '__main__':
#     while True:
#         run()
#         time.sleep(FETCH_INTERVAL)

import pystray

from PIL import Image, ImageDraw


def create_image(width, height, color1, color2):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image


# In order for the icon to be displayed, you must provide an icon
icon = pystray.Icon(
    'test name',
    icon=create_image(64, 64, 'black', 'white'))


# To finally show you icon, call run
icon.run()

s = BlockingScheduler()
s.add_job(run, trigger='interval', seconds=FETCH_INTERVAL, next_run_time=datetime.datetime.now())
s.start()
