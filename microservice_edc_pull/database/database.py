import logging
import time
from sqlalchemy import update


from microservice_edc_pull.constants.constants import ALL_CLASSES
from microservice_edc_pull.constants.database_contants import DATABASE_NAME
from microservice_edc_pull.database.database_connection import DatabaseSession
from microservice_edc_pull.products.products import All_EDC_Product #Don't remove this.
from microservice_edc_pull.parsers.edc_parser import Base,Variant,Price


logger = logging.getLogger('microservice_edc_pull.database')

class Database:
    def __init__(self):
        self.db_name = DATABASE_NAME

    @classmethod
    def start_db_session(cls):
        Base.metadata.create_all(DatabaseSession().engine)

    @classmethod
    def push_products_to_db(cls, filename, *args, method='fill'):
        logger.debug("Starting pushing products to db")
        cls.start_db_session()
        starttime = time.time()

        if method not in ['fill', 'update']:
            raise ValueError("Method not valid")

        # elegant way of saying: "if push_to_db is not given any arguments of which classes to push,
        # then just push everything to the db"
        args = ALL_CLASSES_EDC if args == () else args
        logger.info(f" Pushing {args} to the database!")

        getters = [f"All_EDC_Product.get_products('{arg}','{filename}')"for arg in args]
        for getter in getters:
            file = eval(getter)
            logger.debug(f'{getter} done')

            cls.fill_db(file) if method == 'fill' else cls.merge_db(file)

        logger.info(f'Successfully added {args} to Database in {time.time() - starttime :.2f} seconds!')

    @classmethod
    def fill_db(self,file):
        with DatabaseSession() as session:
            for x in file:
                session.add(x)
                logger.debug(f'Pushed {x} to db')

    @classmethod
    def merge_db(self, file):
        with DatabaseSession() as session:
            for x in file:
                session.merge(x)
                logger.debug(f'Pushed {x} to db')

    def update_db(self, file,table,product_id,dict):
        with DatabaseSession() as session:
            for x in file:
                session.query(table).filter(table.product_id == product_id).update(dict)
                logger.debug(f'Pushed {x} to db')


    @classmethod
    def push_discounts_to_db(cls, method='fill'):
        cls.start_db_session()
        starttime = time.time()

        if method not in ['fill', 'update']:
            raise Exception("Method not valid")

        file = All_EDC_Product.get_discounts()
        cls.fill_db(file) if method == 'fill' else cls.merge_db(file)



        logger.info(f'Successfully added discounts to Database in {time.time() - starttime :.2f} seconds!')

    @classmethod
    def update_stock(cls):
        cls.start_db_session()
        file = All_EDC_Product.get_stock()
        with DatabaseSession() as session:
            logger.info('Updating Stock')
            # todo is this Variant.product_id correct here, doesn't that have to be Variant.variant_id?
            [session.query(Variant).filter(Variant.product_id == x['variant_id'] ).update(x) for x in file]

    @classmethod
    def setup_prices(cls):
        cls.start_db_session()
        file = All_EDC_Product.setup_prices()
        with DatabaseSession() as session:
            logger.info('Setting Up Prices')
            for x in file:
                session.query(Price).filter(Price.product_id == x['product_id']).update(x)

    @classmethod
    def update_prices(cls):
        cls.start_db_session()
        file = All_EDC_Product.get_prices()
        with DatabaseSession() as session:
            logger.info('Updating Prices')
            [session.query(Price).filter(Price.artnr == x['artnr']).update(x) for x in file]
