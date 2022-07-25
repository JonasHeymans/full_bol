from mainapp.microservice_supplier.api.supplier import EdcClient, BigbuyClient
from mainapp.microservice_supplier.parsers.converter import EdcConverter, BigbuyConverter
from scheduler import offer_update
from mainapp.microservice_supplier.adapter.adapter import BigbuyAdapter, EdcAdapter
from support.database.database import EdcDatabase,BigbuyDatabase
from support.logger.logger import Logger

log = Logger().get_commandline_logger('info')

# todo: enum for 'connection_type': merge, update or fill.

#
# bibu = EdcClient()
# bibu.download()
#
# con = EdcConverter()
# con.initial_convert()

# db = EdcDatabase(connection_type='merge')
# db.add_to_db()

bibu = BigbuyClient()
bibu.download()

con = BigbuyConverter()
con.initial_convert()

ad = BigbuyAdapter

db = BigbuyDatabase(connection_type='merge')
db.add_to_db()



