from apscheduler.schedulers.blocking import BlockingScheduler

from support.database.database import Database
from app.microservice_edc_pull.libs.edc import EdcClient
from app.microservice_edc_pull.parsers.converter import Converter
from support.logger.logger import Logger

# TODO remove the XML& pk files once I've pushed to db.
# TODO Break up converter.__loop_through_products into multiple functions/refactor so that it is easier to read
# TODO Check flow of full_product_update when pushing to db, it might be that we push too often (pushing product objects on each new picture)
# TODO drop database every month or so to keep it clean?
# TODO Setup proper logging via Kibana or something?
# TODO Correctly setup calculation of Sell Price
# TODO for prices, variants, properties, measures, categories (and brands?) tables on DB: change primary key to product_id (else we have many prices with all the same information...
# TODO drop duplicates in file of brands,.. speeding up push to db
# TODO: I'm getting the error "Could not add categories of 8765, skipping" and "Something went very wrong in the convert function!"
#  for about 40 categories when pusing to db, though 76 seem to be correctly pushed
# Error when adding product_id as primary key for measures: "sqlalchemy.exc.InvalidRequestError: This Session's transaction has been rolled back due to a previous exception during flush. To begin a new transaction with this Session, first issue Session.rollback(). Original exception was: (raised as a result of Query-invoked autoflush; consider using a session.no_autoflush block if this flush is occurring prematurely)
# (psycopg2.errors.NotNullViolation) null value in column "product_id" of relation "measures" violates not-null constraint
# DETAIL:  Failing row contains (null, null, null, null, null, null)."
# [SQL: INSERT INTO measures (maxdiameter, insertiondepth, weight, packing, length) VALUES (%(maxdiameter)s, %(insertiondepth)s, %(weight)s, %(packing)s, %(length)s)]
# [parameters: {'maxdiameter': None, 'insertiondepth': None, 'weight': None, 'packing': None, 'length': None}]

log = Logger().get_commandline_logger('INFO')

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
    log.info(f'Currently running jobs:')

    for job in sched.get_jobs():
        log.info(f'{job.name.title()}: next run at {job.next_run_time}, trigger for {job.trigger}')

# EDC methods
@sched.scheduled_job('cron', hour=3)
def full_setup():
    edc = EdcClient()
    edc.download_products('full')
    edc.download_products('new')
    edc.download_stock()
    edc.download_discounts()
    edc.download_prices('full')
    edc.download_prices('update')

    con = Converter()
    con.initial_convert('full')
    con.initial_convert('new')
    con.initial_convert('stock')

    db = Database(connection_type='merge')
    db.push_products_to_db('full', 'Product', 'Variant', "Price")

    db.push_products_to_db('new')
    db.push_stock_to_db()
    db.push_discounts_to_db()
    db.setup_prices()
    db.update_prices()


# @sched.scheduled_job('cron', day_of_week='mon', hour=3)
def full_product_update():
    edc = EdcClient()
    edc.download_products('full')

    con = Converter()
    con.initial_convert('full')

    db = Database(connection_type='merge')
    db.push_products_to_db('full')
    db.push_stock_to_db()

    edc.download_discounts()
    db.push_discounts_to_db()

    db.update_prices()


# @sched.scheduled_job('cron', day_of_week='sat', hour=3)
def new_product_update():
    edc = EdcClient()
    edc.download_products('new')

    con = Converter()
    con.initial_convert('new')

    db = Database(connection_type='merge')
    db.push_products_to_db('new')

    # Maybe I don't really need this here, but is not resource intensive so YOLO
    edc.download_discounts()
    db.push_discounts_to_db()


@sched.scheduled_job('cron', minute=30)
def stock_update():
    edc = EdcClient()
    edc.download_stock()

    con = Converter()
    con.initial_convert('stock')

    db = Database(connection_type='merge')
    db.push_stock_to_db()


@sched.scheduled_job('cron', minute=00)
def price_update():
    edc = EdcClient()
    edc.download_prices('full')
    edc.download_prices('update')

    db = Database(connection_type='merge')

    # Setup is probably not necessary here but yolo
    db.setup_prices()
    db.update_prices()

# Bol Methods


