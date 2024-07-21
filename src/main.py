from apscheduler.schedulers.blocking import BlockingScheduler


def run():
    print("running ")


s = BlockingScheduler()
s.add_job(run, trigger='interval', seconds=15)
s.start()
