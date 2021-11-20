from microservice_edc_pull.libs.edc import EdcClient
from microservice_edc_pull.parsers.converter import Converter
from microservice_edc_pull.database.database import Database

# EDC methods

def full_product_update():
    edc = EdcClient()
    edc.download_products('full')

    con = Converter()
    con.initial_convert('full')

    db = Database()
    db.push_products_to_db('full', method='update')

    edc.download_discounts()
    db.push_discounts_to_db()


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


def stock_update():
    edc = EdcClient()
    edc.download_stock()

    con = Converter()
    con.initial_convert('stock')

    db = Database()
    db.push_stock_to_db()


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

