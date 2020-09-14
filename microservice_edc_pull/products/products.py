import logging
import pickle
from typing import List
import csv

logger = logging.getLogger('microservice_edc_pull.products')

from microservice_edc_pull.parsers.edc_parser import Product, Variant, Brand, Measures, Price, Pic, Category, Property, \
    Bulletpoint, Discount  # Don't remove this
from microservice_edc_pull.parsers.converter import Converter
from microservice_edc_pull.constants.save_locations import RAW_PATH, CONVERTED_FILE_PATH


class AllEdcProduct:

    def __open_pickle(self, file_path):
        with open(f'{file_path}.pkl', 'rb') as f:
            logger.debug(f"Opening {file_path}")
            return pickle.load(f)

    # TODO probably will want this little converting part that I still do here also in the converter class instead of
    #  here. Best method is I think just to create a separate file in dict for each class.

    def get_products(self, classname: str, filename: str) -> List:
        file = self.__open_pickle(f"{CONVERTED_FILE_PATH}{filename}")
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


    def get_discounts(self) -> List:
        with open(f'{RAW_PATH}discounts.csv', newline='') as f:
            reader = csv.reader(f, delimiter=';')
            file = list(reader)[1:]

        return [Discount(e) for e in file]


    def get_stock(self) -> List:
        file = self.__open_pickle(f"{CONVERTED_FILE_PATH}stock")['producten']['product']
        con = Converter()

        return con.convert_stock(file)


    def setup_prices(self):
        with open('files/feeds/price_full.csv', 'r') as csv_file:
            file = csv.DictReader(csv_file, delimiter=';')
            con = Converter()
            return con.convert_prices_setup(file)


    def get_prices(self):
        with open('files/feeds/price_update.csv', 'r') as csv_file:
            file = csv.DictReader(csv_file, delimiter=';')
            con = Converter()
            return con.convert_prices(file)
