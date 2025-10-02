import datetime as dt

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import func

from mainapp.microservice_bol.retailer.api.api import RetailerAPI
from mainapp.microservice_both.parsers.edc_order import EdcShipment
from mainapp.microservice_supplier.api.supplier import BigbuyClient
from mainapp.microservice_supplier.parsers.converter import BigbuyConverter
from mainapp.microservice_supplier.parsers.base_classes import Product, Variant
from support.database.database import BolDatabase, BigbuyDatabase
from support.database.database_connection import DatabaseSession
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
# (psycopg2.errors.NotNullViolation) @null value in column "product_id" of relation "measures" violates not-null constraint
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
    bibu = BigbuyClient()
    bibu.download()

    con = BigbuyConverter()
    con.initial_convert()

    db = BigbuyDatabase(connection_type='merge')
    db.add_to_db()


# @sched.scheduled_job('cron', day_of_week='mon', hour=3)
def full_product_update():
    pass
    # TODO: bol-side implementation


# @sched.scheduled_job('cron', day_of_week='sat', hour=3)
def new_product_update():
    pass

    # TODO: bol-side implementation


@sched.scheduled_job('cron', minute=30)
def stock_update():
    pass

    # TODO: bol-side implementation


@sched.scheduled_job('cron', minute=00)
def update_price():
    pass

    # TODO: bol-side implementation


# Bol Methods
def order_update():
    ## Retrieve orders from bol and to db

    db = BolDatabase(connection_type='merge')
    db.push_orders_to_db()

    ## Optional: cancel canceled items on EDC, and update in our db accordingly

    ## Order orders at EDC

    ## Confirm shipment on bol.com and choose shipment


def offer_update():
    # Get bol offers
    api = RetailerAPI(demo=False)
    api.login()
    current_offers = api.offers.list()


    # Get offers from db
    with DatabaseSession() as session:
        today = dt.datetime.today().date()
        new_offers = session.query(Variant) \
            .join(Product, Product.product_id == Variant.product_id) \
            .filter(Variant.stock > 5,
                    Variant.sellprice < 100,
                    func.date(Variant.update_date_stock) == today
                    ).all()
        print(new_offers)


@sched.scheduled_job('interval', minutes=15)
def add_tracking():
    # Retrieve tracking information from EDC: done by flask server

    # Check which orders in db lack tracking information

    with DatabaseSession() as session:
        shipments = session.query(EdcShipment).filter(
            (EdcShipment.status == 'shipped') & (EdcShipment.send_to_bol == False)).all()

    # Send new tracking information to bol.com and update in our db
    api = RetailerAPI()
    api.login()
    for shipment in shipments:
        if hasattr(shipment, 'new_ordernumber'):
            shipment.ordernumber = shipment.new_ordernumber

        api.orders.ship_order_item(order_item_id=shipment.own_ordernumber,
                                   shipment_reference=shipment.ordernumber,
                                   shipping_label_code=None,
                                   transporter_code='TNT',
                                   track_and_trace=shipment.tracktrace)
