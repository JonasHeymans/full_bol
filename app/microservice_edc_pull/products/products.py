import csv
import logging
import pickle
from typing import List

logger = logging.getLogger('microservice_edc_pull.products')

from app.microservice_edc_pull.parsers.edc_parser import Product, Variant, Brand, Measures, Price, Pic, Category, \
    Property, \
    Bulletpoint, Discount  # Don't remove this
from app.microservice_edc_pull.parsers.converter import Converter
from app.microservice_edc_pull import BASE_PATH


class AllEdcProduct:

    def __open_pickle(self, file_path):
        with open(f'{file_path}.pkl', 'rb') as f:
            logger.debug(f"Opening {file_path}")
            return pickle.load(f)

    # TODO probably will want this little converting part that I still do here also in the converter class instead of
    #  here. Best method is I think just to create a separate file in dict for each class.

    def get_products(self, classname: str, filename: str) -> List:
        file = self.__open_pickle(f"{BASE_PATH}/files/dict/{filename}")
        d = {
            'Category': 'categories',
            'Variant': 'variants',
            'Pic': 'pics',
            'Property': 'properties',
            'Bulletpoint': 'bulletpoints'
        }
        if classname in d.keys():
            conv = Converter()
            file = conv.convert(file, d[classname])

        logger.debug(f'Starting parsing of {classname}')

        classes = {'Product': Product,
                   'Variant': Variant,
                   'Brand': Brand,
                   'Category': Category,
                   'Measures': Measures,
                   'Property': Property,
                   'Bulletpoint': Bulletpoint,
                   'Pic': Pic,
                   'Stock': Variant,
                   'Price': Price,
                   'Discount': Discount}

        class_objects = [classes[classname](e) for e in file]

        if classname == 'Price':
            for price_obj, e in zip(class_objects, file):
                price_obj.add_init_attibutes(e)

        return class_objects

    def get_discounts(self) -> List:
        with open(f'{BASE_PATH}/files/feeds/discounts.csv', newline='') as f:
            reader = csv.reader(f, delimiter=';')
            file = list(reader)[1:]

        return [Discount(e) for e in file]

    def get_stock(self) -> List:
        input_file = self.__open_pickle(f"{BASE_PATH}/files/dict/stock")['producten']['product']
        con = Converter()

        file = con.convert_stock(input_file)

        stock_objects = [Variant(e) for e in file]

        for stock_object in stock_objects:
            stock_object.stock_update()

        return stock_objects

    def setup_prices(self):
        with open(f'{BASE_PATH}/files/feeds/price_full.csv', 'r') as csv_file:
            input_file = csv.DictReader(csv_file, delimiter=';')
            con = Converter()

            file = con.convert_prices(input_file, 'setup')
            price_objects = [Price(e) for e in file]

            for price_obj, e in zip(price_objects, file):
                price_obj.add_setup_attibutes(e)

            return price_objects

    def update_prices(self):
        with open(f'{BASE_PATH}/files/feeds/price_update.csv', 'r') as csv_file:
            input_file = csv.DictReader(csv_file, delimiter=';')
            con = Converter()

            file = con.convert_prices(input_file, 'update')
            price_objects = [Price(e) for e in file]

            for price_obj, e in zip(price_objects, file):
                price_obj.add_update_attibutes(e)

            return price_objects
