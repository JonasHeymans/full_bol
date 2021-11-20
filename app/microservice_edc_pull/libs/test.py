from app.microservice_edc_pull.database.database import Database
from app.microservice_edc_pull.libs.edc import EdcClient
from app.microservice_edc_pull.parsers.converter import Converter

def full_product_update():
    edc = EdcClient()
    edc.download_products('full')

    con = Converter()
    con.initial_convert('full')

    db = Database()
    db.push_products_to_db('full', method='update')

    edc.download_discounts()
    db.push_discounts_to_db()

import os
os.chdir('/Users/peter/PycharmProjects')
print(os.path.abspath(os.curdir))

full_product_update()