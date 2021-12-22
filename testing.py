from app.microservice_edc_pull.database.database import Database
from support.logger.logger import Logger

log = Logger().get_commandline_logger('info')

# Todo: when full/new is added, also update the update_stock field
# todo what's "minprice"? (I saw it as an attribute in the raw files)


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

db = Database()

#
db.push_stock_to_db(method='merge')
db.push_discounts_to_db(method='merge')
db.setup_prices(method='merge')
db.update_prices(method='merge')
