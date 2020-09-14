from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from datetime import date
import os
import time


if __name__ == '__main__':
    scheduler = BackgroundScheduler()

    scheduler.add_job()


    scheduler.start()

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()