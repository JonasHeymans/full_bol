from support.database.database import EdcDatabase, DatabaseSession
from mainapp.microservice_edc_pull.api.edc import EdcClient
from mainapp.microservice_edc_pull.parsers.converter import Converter

from scheduler import order_update
from support.logger.logger import Logger
from mainapp.microservice_bol.retailer.api.api import RetailerAPI
from mainapp.microservice_both.parsers.edc_order import EdcShipment
from scheduler import offer_update, full_setup

log = Logger().get_commandline_logger('info')

# Todo: when full/new is added, also update the update_stock field
# todo: enum for 'connection_type': merge, update or fill.
#
#
# edc = EdcClient()
# edc.download_products('full')
# edc.download_products('new')
# edc.download_stock()
# edc.download_discounts()
# edc.download_prices('full')
# edc.download_prices('update')
#
# con = Converter()
# con.initial_convert('full')
# con.initial_convert('new')
# con.initial_convert('stock')
#
db = EdcDatabase(connection_type='merge')
# db.push_products_to_db('full', 'Product', 'Variant', "Price")
# db.push_products_to_db('new')
# db.push_stock_to_db()
# db.push_discounts_to_db()
# db.push_full_prices_to_db()
# db.push_new_prices_to_db()

full_setup()