import logging
import time

from decouple import config
from sqlalchemy.exc import IntegrityError

from app.microservice_edc_pull import ALL_CLASSES
from app.microservice_edc_pull.parsers.edc_parser import Base as EdcBase, Product, Variant, Price, Brand, Category, Measures, \
    Property, Bulletpoint, Pic, Discount
from app.microservice_edc_pull.products.products import AllEdcProduct

from support.database.database_connection import DatabaseSession

from app.microservice_bol.retailer.models.models import Base as BolBase


logger = logging.getLogger('microservice_edc_pull.database')


def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


class Database:
    def __init__(self, connection_type):
        self.DATABASE_URL = config('DATABASE_URL')
        self.connection_type = connection_type
        self.__start_db_session()

    @property
    def connection_type(self):
        return self.__connection_type

    @connection_type.setter
    def connection_type(self, value):
        if value not in ['merge', 'update', 'fill']:
            raise NameError('Name must be in (merge', 'update', 'fill)')

        self.__connection_type = value

    def __start_db_session(self):
        EdcBase.metadata.create_all(DatabaseSession().engine)
        BolBase.metadata.create_all(DatabaseSession().engine)


    def __push_to_df(self, lst, update_target_id, update_target_class):
        try:
            with DatabaseSession() as session:
                for item in lst:
                    target_id = getattr(item, update_target_id.key)
                    attributes = {key: vars(item)[key] for key in vars(item) if key != '_sa_instance_state'}
                    try:
                        if self.connection_type == 'fill':
                            session.add(item)
                        elif self.connection_type == 'merge':
                            session.merge(item)
                        elif self.connection_type == 'update':
                            session.query(update_target_class).filter(update_target_id == target_id).update(
                                attributes)
                        logger.debug(f'Pushed {item} to db')

                    except IntegrityError as e:
                        error_item_location = lst.index(item) - 1
                        error_item = lst[error_item_location]
                        logger.debug(f'IntegrityError on {error_item}')
                        session.rollback()

                        if f'(product_id)=({error_item.product_id}) is not present in table "products".'\
                                in e.args[0]:

                            product_item = error_item.extract_product()

                            session.merge(product_item)
                            session.commit()

                            session.merge(error_item)

                        elif f'(artnr)=({error_item.artnr}) is not present in table "products".' in e.args[0]:
                            product_item = error_item.extract_product()
                            variant_item = error_item.extract_variant()

                            session.merge(product_item)
                            session.commit()

                            session.merge(variant_item)
                            session.commit()

                            session.merge(error_item)

                        else:
                            logger.warning(f'IntegrityError: {e} \n')

        except Exception as e:
            logger.warning(f'Unsolvable error on {item}: {e}\n')
            session.rollback()

    def insert_in_db(self, file, update_target=None):
        starttime = time.time()

        update_targets = {'product': [Product, 'product_id'],
                          'variant': [Variant, 'variant_id'],
                          'brand': [Brand, 'brand_id'],
                          'category': [Category, 'category_id'],
                          'measures': [Measures, 'product_id'],
                          'property': [Property, 'propid'],
                          'bulletpoint': [Bulletpoint, 'bp'],
                          'pic': [Pic, 'pic'],
                          'stock': [Variant, 'variant_id'],
                          'price': [Price, 'artnr'],
                          'discount': [Discount, 'brand_id']}

        update_target_class = update_targets[update_target][0]
        update_target_id = getattr(update_target_class, update_targets[update_target][1])

        new_lst = split_list(file, 500)
        for lst in new_lst:
            self.__push_to_df(lst, update_target_id, update_target_class)
            logger.info(f'Completed {new_lst.index(lst) + 1} of {len(new_lst)}')

        logger.info(f'Successfully added {update_target} to Database in {(time.time() - starttime) / 60 :.2f} minutes!')

    def push_products_to_db(self, filename, *args):
        logger.debug("Starting pushing products to db")
        full_starttime = time.time()

        # elegant way of saying: "if insert_in_db is not given any arguments of which classes to push,
        # then just push everything to the db"
        args = ALL_CLASSES if args == () else args
        logger.info(f" Pushing {args} to the database!")

        for arg in args:
            edcpr = AllEdcProduct()
            file = edcpr.get_products(classname=arg, filename=filename)

            logger.info(f'Starting on {arg}')

            self.insert_in_db(file, update_target=arg.lower())

        logger.info(f'Successfully added {args} to Database in {(time.time() - full_starttime) / 60 :.2f} minutes!')

    def push_discounts_to_db(self):
        aep = AllEdcProduct()
        file = aep.get_discounts()
        logger.info('Pushing Discounts')
        self.insert_in_db(file,  update_target='discount')

    def push_stock_to_db(self):
        aep = AllEdcProduct()
        file = aep.get_stock()
        logger.info('Updating Stock')
        self.insert_in_db(file, update_target='stock')

    def setup_prices(self):
        aep = AllEdcProduct()
        file = aep.setup_prices()
        logger.info('Setting Up Prices')
        self.insert_in_db(file, update_target='price')

    def update_prices(self):
        aep = AllEdcProduct()
        file = aep.update_prices()
        logger.info('Updating Prices')
        self.insert_in_db(file, update_target='price')


