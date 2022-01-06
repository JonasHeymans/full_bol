from support.database.database import EdcDatabase, DatabaseSession
from app.microservice_edc_pull.api.edc import EdcClient
from app.microservice_edc_pull.parsers.converter import Converter

from scheduler import order_update
from support.logger.logger import Logger
from app.microservice_bol.retailer.api.api import RetailerAPI
from app.microservice_both.parsers.edc_order import EdcShipment

log = Logger().get_commandline_logger('info')

# Todo: when full/new is added, also update the update_stock field
# todo what's "minprice"? (I saw it as an attribute in the raw files)
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
# db = EdcDatabase(connection_type='merge')

