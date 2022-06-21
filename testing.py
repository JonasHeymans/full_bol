from mainapp.microservice_supplier.api.supplier import EdcClient, BigbuyClient
from mainapp.microservice_supplier.parsers.converter import EdcConverter, BigbuyConverter
from scheduler import offer_update
from support.database.database import EdcDatabase,BigbuyDatabase
from support.logger.logger import Logger

log = Logger().get_commandline_logger('info')

# todo: enum for 'connection_type': merge, update or fill.


bibu = EdcClient()
bibu.download()

con = EdcConverter()
con.initial_convert()

db = BigbuyDatabase(connection_type='merge')
db.add_to_db()





