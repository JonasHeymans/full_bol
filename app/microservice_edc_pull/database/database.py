import logging
import time

from decouple import config

from app.microservice_edc_pull import ALL_CLASSES
from app.microservice_edc_pull.parsers.edc_parser import Base, Variant, Price
from app.microservice_edc_pull.products.products import AllEdcProduct  # Don't remove this.
from support.database.database_connection import DatabaseSession

logger = logging.getLogger('microservice_edc_pull.database')


def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


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

        for arg in args:
            edcpr = AllEdcProduct()
            file = edcpr.get_products(classname=arg, filename=filename)

            logger.info(f'Starting on {arg}')

            self.fill_db(file) if method == 'fill' else self.merge_db(file)

            intervalttime = time.time()
            logger.info(f'{arg} done, took {intervalttime - starttime :.2f} seconds')


        logger.info(f'Successfully added {args} to Database in {time.time() - starttime :.2f} seconds!')


    def fill_db(self, file):
        new_lst = split_list(file, 500)
        for lst in new_lst:
            try:
                with DatabaseSession() as session:
                    for x in lst:
                        session.add(x)
                        logger.debug(f'Pushed {x} to db')
            except:
                session.rollback()

        # for lst in new_lst:
        #     with DatabaseSession() as session:
        #         try:
        #             session.add_all(lst)
        #             logger.debug(f'Pushed {file.index(lst[0])} of {len(file)} to db')
        #         except Exception as e:
        #             logger.error(e)
        #             continue

    def merge_db(self, file):
        new_lst = split_list(file, 500)
        for lst in new_lst:
            with DatabaseSession() as session:
                for x in lst:
                    try:
                        logger.info(f'Completed {new_lst.index(lst)} of {len(new_lst)}')
                        session.merge(x)
                        logger.debug(f'Pushed {x} to db')
                    except Exception as e:
                        session.rollback()
                        logger.warning(f'Error on {x}: {e}')

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
                logger.debug(f'Pushed {x} to db')
                session.query(Price).filter(Price.product_id == x['product_id']).update(x)

    def push_prices_to_db(self):
        self.__start_db_session()
        aep = AllEdcProduct()
        file = aep.get_prices()
        with DatabaseSession() as session:
            logger.info('Updating Prices')
            [session.query(Price).filter(Price.artnr == x['artnr']).update(x) for x in file]
