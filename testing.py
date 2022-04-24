from mainapp.microservice_supplier.api.supplier import EdcClient
from mainapp.microservice_supplier.parsers.converter import EdcConverter
from scheduler import offer_update
from support.database.database import EdcDatabase
from support.logger.logger import Logger

log = Logger().get_commandline_logger('info')

# todo: enum for 'connection_type': merge, update or fill.
#

# edc = EdcClient()
# edc.download()
#
# con = EdcConverter()
# con.initial_convert()

db = EdcDatabase(connection_type='merge')
db.add_to_db()





