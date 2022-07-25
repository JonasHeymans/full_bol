import csv
import logging
import pickle
from typing import List

logger = logging.getLogger(__name__)

from mainapp.microservice_supplier import ALL_EDC_CLASSES,ALL_BIGBUY_CLASSES, Product, Variant
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
    #  here. Best method is I think just to create a separate file in cleaned for each class.

    def get_products(self) -> List:
        file = self.open_pickle(f"{BASE_PATH}/files/{self.supplier}/cleaned/products")

        logger.debug(f'Starting parsing of products')

        class_objects = [Product(e, self.supplier) for e in file]

        return class_objects

    def get_variants(self) -> List:
        file = self.open_pickle(f"{BASE_PATH}/files/{self.supplier}/cleaned/variants")

        logger.debug(f'Starting parsing of variants')

        class_objects = [Variant(e, self.supplier) for e in file]

        return class_objects



    # TODO: EDC legacy?
    def get_stock(self) -> List:
        file = self.open_pickle(f"{BASE_PATH}/files/{self.supplier}/cleaned/stock")

        stock_objects = [Variant(e,self.supplier) for e in file]

        for stock_object in stock_objects:
            stock_object.stock_update()

        return stock_objects


class EdcAdapter(Adapter):
    def __init__(self):
        self.supplier = 'edc'
        self.classes = ALL_EDC_CLASSES

        super().__init__(self.supplier, self.classes)

class BigbuyAdapter(Adapter):
    def __init__(self):
        self.supplier = 'bigbuy'
        self.classes = ALL_BIGBUY_CLASSES

        super().__init__(self.supplier, self.classes)