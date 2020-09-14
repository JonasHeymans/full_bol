import logging
import pickle
from typing import List
import csv

logger = logging.getLogger('microservice_edc_pull.products')

from microservice_edc_pull.parsers.edc_parser import Product, Variant, Brand, Measures, Price, Pic, Category, Property, \
    Bulletpoint, Discount  # Don't remove this
from microservice_edc_pull.parsers.converter import Converter
from microservice_edc_pull.constants.save_locations import *


class All_EDC_Product:

    @classmethod
    def __open_pickle(cls, file_path):
        with open(f'{file_path}.pkl', 'rb') as f:
            logger.debug(f"Opening {file_path}")
            return pickle.load(f)

    # TODO probably will want this little converting part that I still do here also in the converter class instead of
    #  here. Best method is I think just to create a separate file in dict for each class.
    @classmethod
    def get_products(cls, classname: str, filename: str) -> List:
        file = cls.__open_pickle(f"{CONVERTED_FILE_PATH}{filename}")
        d = {
            'Category': 'categories',
            'Variant': 'variants',
            'Pic': 'pics',
            'Property': 'properties',
            'Bulletpoint': 'bulletpoints'
        }
        if classname in d.keys():
            file = Converter.convert(file, d[classname])

        logger.debug(f'Starting parsing of {classname}')

        getter = f'[{classname}(e) for e in file]'
        return eval(getter)

    @classmethod
    def get_discounts(cls) -> List:
        with open(f'{RAW_PATH}discounts.csv', newline='') as f:
            reader = csv.reader(f, delimiter=';')
            file = list(reader)[1:]

        getter = f'[Discount(e) for e in file]'
        return eval(getter)

    @classmethod
    def get_stock(cls) -> List:
        file = cls.__open_pickle(f"{CONVERTED_FILE_PATH}stock")['producten']['product']
        return Converter.convert_stock(file)

    @classmethod
    def setup_prices(cls):
        with open('files/feeds/price_full.csv', 'r') as csv_file:
            file = csv.DictReader(csv_file, delimiter=';')
            return Converter.convert_prices_setup(file)

    @classmethod
    def get_prices(cls):
        with open('files/feeds/price_update.csv', 'r') as csv_file:
            file = csv.DictReader(csv_file, delimiter=';')
            return Converter.convert_prices(file)
