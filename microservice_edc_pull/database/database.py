import logging
import time

from decouple import config

from database_connection import DatabaseSession
from microservice_edc_pull import ALL_CLASSES
from microservice_edc_pull.parsers.edc_parser import Base, Variant, Price
from microservice_edc_pull.products.products import AllEdcProduct  # Don't remove this.

logger = logging.getLogger('microservice_edc_pull.database')


class Database:
    def __init__(self):
        self.DATABASE_URL = config('DATABASE_URL')

    def __start_db_session(self):
        Base.metadata.create_all(DatabaseSession().engine)

    def push_products_to_db(self, filename, method='fill', *args):
        logger.debug("Starting pushing products to db")
        self.__start_db_session()
        starttime = time.time()

        if method not in ['fill', 'update']:
            raise ValueError("Method not valid")

        # elegant way of saying: "if push_to_db is not given any arguments of which classes to push,
        # then just push everything to the db"
        args = ALL_CLASSES if args == () else args
        logger.info(f" Pushing {args} to the database!")

        getters = [f"edcpr.get_products(classname='{arg}', filename='{filename}')" for arg in args]
        for getter in getters:
            edcpr = AllEdcProduct()
            file = eval(getter)
            logger.debug(f'{getter} done')

            self.fill_db(file) if method == 'fill' else self.merge_db(file)

        logger.info(f'Successfully added {args} to Database in {time.time() - starttime :.2f} seconds!')

    def fill_db(self, file):
        with DatabaseSession() as session:
            for x in file:
                session.add(x)
                logger.debug(f'Pushed {x} to db')

    def merge_db(self, file):
        with DatabaseSession() as session:
            for x in file:
                try:
                    session.merge(x)
                    logger.debug(f'Pushed {x} to db')
                except Exception as e:
                    logger.error(e)
                    continue

    def update_db(self, file, table, product_id, dict):
        with DatabaseSession() as session:
            for x in file:
                session.query(table).filter(table.product_id == product_id).update(dict)
                logger.debug(f'Pushed {x} to db')

    def push_discounts_to_db(self, method='fill'):
        self.__start_db_session()
        starttime = time.time()

        if method not in ['fill', 'update']:
            raise Exception("Method not valid")

        aep = AllEdcProduct()
        file = aep.get_discounts()
        self.fill_db(file) if method == 'fill' else self.merge_db(file)

        logger.info(f'Successfully added discounts to Database in {time.time() - starttime :.2f} seconds!')

    def push_stock_to_db(self):
        self.__start_db_session()
        aep = AllEdcProduct()
        file = aep.get_stock()
        with DatabaseSession() as session:
            logger.info('Updating Stock')

            # todo is this Variant.product_id correct here, doesn't that have to be Variant.variant_id?
            [session.query(Variant).filter(Variant.product_id == x['variant_id']).update(x) for x in file]

    def setup_prices(self):
        self.__start_db_session()
        aep = AllEdcProduct()
        file = aep.setup_prices()
        with DatabaseSession() as session:
            logger.info('Setting Up Prices')
            for x in file:
                session.query(Price).filter(Price.product_id == x['product_id']).update(x)

    def push_prices_to_db(self):
        self.__start_db_session()
        aep = AllEdcProduct()
        file = aep.get_prices()
        with DatabaseSession() as session:
            logger.info('Updating Prices')
            [session.query(Price).filter(Price.artnr == x['artnr']).update(x) for x in file]
