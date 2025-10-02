import os
from mainapp.microservice_supplier.api.supplier import EdcClient, BigbuyClient
from mainapp.microservice_supplier.parsers.converter import EdcConverter, BigbuyConverter
from mainapp.microservice_supplier.adapter.adapter import BigbuyAdapter, EdcAdapter
from support.database.database import EdcDatabase, BigbuyDatabase, BolDatabase
from support.logger.logger import Logger
from scheduler import offer_update

log = Logger().get_commandline_logger('info')

# todo: enum for 'connection_type': merge, update or fill.

# bibu = BigbuyClient()
# bibu.download()


con = BigbuyConverter()
con.initial_convert()

db = BigbuyDatabase(connection_type='merge')
db.add_to_db()

# from mainapp.microservice_bol.retailer.api.api import RetailerAPI
# api = RetailerAPI(demo=False)
# api.login()

# tmp = api.offers.get_export_file()

# print('lo')
# db = BolDatabase(connection_type='merge')
# db.add_to_db()

