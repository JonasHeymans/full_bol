import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

from support.logger.logger import Logger

from app.microservice_edc_pull.database.database import Database
from app.microservice_edc_pull.libs.edc import EdcClient
from app.microservice_edc_pull.parsers.converter import Converter

# TODO remove the dirty 'eval's everywhere
# TODO remove the XML& pk files once I've pushed to db.
# TODO Break up converter.__loop_through_products into multiple functions/refactor so that it is easier to read
# TODO Remove products that are out of stock?
# TODO Check flow of full_product_update when pushing to db, it might be that we push too often (pushing product objects on each new picture)

log = Logger().get_commandline_logger('DEBUG')

'''
Timings of each request:


- Full: weekly. To fill db initially, update prices / product properties and check for discontinued products.
- New: Every Friday night. To add new products
- Stock: Every hour. To keep stock up to date.
- Discounts: weekly. To change awarded discounts. 

'''

sched = BlockingScheduler()

# General methods
@sched.scheduled_job('interval', minutes=10)
def up_reminder():
    log.info(f'Still running at {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')
    log.info(os.path.abspath(os.curdir))

# EDC methods

# @sched.scheduled_job('cron', day_of_week='mon', hour=3)
@sched.scheduled_job('cron', second=30)
def full_product_update():
    edc = EdcClient()
    edc.download_products('full')

    con = Converter()
    con.initial_convert('full')

    db = Database()
    db.push_products_to_db('full', method='update')

    edc.download_discounts()
    db.push_discounts_to_db()


@sched.scheduled_job('cron', hour=3)
def new_product_update():
    edc = EdcClient()
    edc.download_products('new')

    con = Converter()
    con.initial_convert('new')

    db = Database()
    db.push_products_to_db('new')

    # Maybe i don't really need this here, but is not resource intensive so YOLO
    edc.download_discounts()
    db.push_discounts_to_db()


@sched.scheduled_job('cron', minute=30)
def stock_update():
    edc = EdcClient()
    edc.download_stock()

    con = Converter()
    con.initial_convert('stock')

    db = Database()
    db.push_stock_to_db()

@sched.scheduled_job('cron', minute=00)
def price_update(*args):
    # args can be 'full' or 'update'
    scope = 'full' if args == () else args

    edc = EdcClient()
    edc.download_prices(scope)

    db = Database()
    if scope == 'full':
        db.setup_prices()
    if scope == 'update':
        db.push_prices_to_db()


# Bol Methods

sched.start()
