import csv
import logging
import pickle
from typing import List

logger = logging.getLogger(__name__)

from mainapp.microservice_supplier import ALL_EDC_CLASSES, EdcVariant, EdcPrice, EdcDiscount
from mainapp.microservice_supplier.parsers.converter import Converter
from mainapp.microservice_supplier import BASE_PATH


class Adapter:
    def __init__(self, supplier, classes):
        self.supplier = supplier
        self.classes = classes

    def open_pickle(self, file_path):
        with open(f'{file_path}.pkl', 'rb') as f:
            logger.debug(f"Opening {file_path}")
            return pickle.load(f)

    # TODO probably will want this little converting part that I still do here also in the converter class instead of
    #  here. Best method is I think just to create a separate file in dict for each class.

    def get_products(self, classname: str, filename: str) -> List:
        file = self.open_pickle(f"{BASE_PATH}/files/{self.supplier}/dict/{filename}")
        to_convert = {
            'Category': 'categories',
            'Variant': 'variants',
            'Pic': 'pics',
            'Property': 'properties',
            'Bulletpoint': 'bulletpoints'
        }
        if classname in to_convert.keys():
            conv = Converter(self.supplier)
            file = conv.convert(file, to_convert[classname])

        logger.debug(f'Starting parsing of {classname}')

        class_objects = [self.classes[classname](row) for row in file]

        if classname == 'Price':
            for price_obj, e in zip(class_objects, file):
                price_obj.add_init_attibutes(e)

        if classname == 'Variant':
            for stock_object, e in zip(class_objects, file):
                stock_object.stock_update()

        return class_objects

    def get_discounts(self) -> List:
        with open(f'{BASE_PATH}/files/{self.supplier}/feeds/discounts.csv', newline='') as f:
            reader = csv.reader(f, delimiter=';')
            file = list(reader)[1:]

        if self.supplier == 'edc':
            Discount = EdcDiscount

        return [Discount(e) for e in file]

    def get_stock(self) -> List:
        input_file = self.open_pickle(f"{BASE_PATH}/files/{self.supplier}/dict/stock")['producten']['product']
        con = Converter(self.supplier)

        file = con.convert_stock(input_file)

        if self.supplier == 'edc':
            Variant = EdcVariant

        stock_objects = [Variant(e) for e in file]

        for stock_object in stock_objects:
            stock_object.stock_update()

        return stock_objects

    def setup_prices(self):
        with open(f'{BASE_PATH}/files/{self.supplier}/feeds/full_price.csv', 'r') as csv_file:
            input_file = csv.DictReader(csv_file, delimiter=';')
            con = Converter(self.supplier)

            if self.supplier == 'edc':
                Price = EdcPrice

            file = con.convert_prices(input_file, 'setup')
            price_objects = [Price(e) for e in file]

            for price_obj, e in zip(price_objects, file):
                price_obj.add_setup_attibutes(e)

            return price_objects

    def update_prices(self):
        with open(f'{BASE_PATH}/files/{self.supplier}/feeds/update_price.csv', 'r') as csv_file:
            input_file = csv.DictReader(csv_file, delimiter=';')
            con = Converter(self.supplier)

            if self.supplier == 'edc':
                Price = EdcPrice

            file = con.convert_prices(input_file, 'update')
            price_objects = [Price(e) for e in file]

            for price_obj, e in zip(price_objects, file):
                price_obj.add_update_attibutes(e)

            return price_objects


class EdcAdapter(Adapter):
    def __init__(self):
        self.supplier = 'edc'
        self.classes = ALL_EDC_CLASSES

        super().__init__(self.supplier, self.classes)
