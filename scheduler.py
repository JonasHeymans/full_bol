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
# TODO drop database every month or so to keep it clean?
# TODO Setup proper logging via Kibana or something?
# TODO Correctly setup calculation of Sell Price
# TODO for prices, variants, properties, measures, categories (and brands?) tables on DB: change primary key to product_id (else we have many prices with all the same information...


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
    log.info(f'All Good at {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')

# EDC methods
def initial_setup():
    # This function is still very much incomplete


    db = Database()
    db.push_products_to_db('full', method='update')

    db.setup_prices()



@sched.scheduled_job('cron', day_of_week='mon', hour=3)
def full_product_update():
    edc = EdcClient()
    edc.download_products('full')

    con = Converter()
    con.initial_convert('full')


    edc.download_discounts()
    db.push_discounts_to_db(method='update')


@sched.scheduled_job('cron', day_of_week='sat', hour=3)
def new_product_update():
    edc = EdcClient()
    edc.download_products('new')

    con = Converter()
    con.initial_convert('new')

    db = Database()
    db.push_products_to_db('new', method='update')

    # Maybe i don't really need this here, but is not resource intensive so YOLO
    edc.download_discounts()
    db.push_discounts_to_db(method='update')


@sched.scheduled_job('cron', minute=30)
def stock_update():
    edc = EdcClient()
    edc.download_stock()

    con = Converter()
    con.initial_convert('stock')

    db = Database()
    db.push_stock_to_db()

@sched.scheduled_job('cron', minute=00)
def price_update():

    edc = EdcClient()
    edc.download_prices('update')

    db = Database()
    db.push_prices_to_db()


# Bol Methods

sched.start()
