from app.microservice_edc_pull.database.database import Database
from app.microservice_edc_pull.libs.edc import EdcClient
from app.microservice_edc_pull.parsers.converter import Converter
from support.logger.logger import Logger

log = Logger().get_commandline_logger('info')

# Todo: when full/new is added, also update the update_stock field
# todo what's "minprice"? (I saw it as an attribute in the raw files)
# todo: enum for 'connection_type': merge, update or fill.
#
#
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
db.push_products_to_db('full', 'Product', 'Variant',
                       "Price")

db.push_products_to_db('new')
db.push_stock_to_db()
db.push_discounts_to_db()
db.setup_prices()
db.update_prices()
