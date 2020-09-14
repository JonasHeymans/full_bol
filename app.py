import time

from apscheduler.schedulers.background import BackgroundScheduler

from scheduler import full_product_update, new_product_update, stock_update, price_update

if __name__ == '__main__':
    scheduler = BackgroundScheduler({'apscheduler.timezone': 'UTC'})

    # Full db update (removing discontiunued products) every Monday night
    scheduler.add_job(full_product_update(),
                      'con',
                      day_of_week='mon',
                      hour=1)

    # New product update every 3 days
    scheduler.add_job(new_product_update(), 'interval', days=3)

    # Stock and price update every hour
    scheduler.add_job(stock_update, 'interval', hours=1)
    scheduler.add_job(price_update('update'), 'interval', hours=1)

    scheduler.add_job()
    scheduler.add_job()
    scheduler.add_job()

    scheduler.start()

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
