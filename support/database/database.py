import logging
import os
import time

from decouple import config
from sqlalchemy.exc import IntegrityError

from mainapp.microservice_bol.adapter.adapter import BolAdapter
from mainapp.microservice_bol.parsers.bol_classes import Base as BolBase, Order, Shipment, shipmentDetails, OrderItem, \
    billingDetails
from mainapp.microservice_both.adapter.adapter import OrderAdapter
from mainapp.microservice_both.parsers.edc_order import Base as OrderBase, EdcShipment
from mainapp.microservice_supplier import BASE_PATH, ALL_EDC_CLASSES, ALL_BIGBUY_CLASSES
from mainapp.microservice_supplier.adapter.adapter import Adapter
from mainapp.microservice_supplier.parsers.base_classes import Base as EdcBase, Product, Variant
from support.database.database_connection import DatabaseSession

logger = logging.getLogger('microservice_supplier.database')


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
        OrderBase.metadata.create_all(DatabaseSession().engine)

    def __push_to_db(self, lst, update_target_id, update_target_class):
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
                        try:
                            error_item_location = lst.index(item) - 1
                            error_item = lst[error_item_location]
                            logger.debug(f'IntegrityError on {error_item}')
                            session.rollback()

                            if f'(product_id)=({error_item.product_id}) is not present in table' in e.args[0]:

                                product_item = Product(parent={'id': error_item.product_id,
                                                               'name': 'Not found'},
                                                       supplier=error_item.supplier)

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

                        except Exception as e:
                            logger.warning(f'IntegrityError: {e} \n')

        except Exception as e:
            logger.warning(f'Unsolvable error on {item}: {e}\n')
            session.rollback()

    def insert_in_db(self, file, update_target=None):
        starttime = time.time()

        update_targets = {'product': [Product, 'product_id'],
                          'variant': [Variant, 'id'],
                          'stock': [Variant, 'variant_id'],
                          'order': [Order, 'orderId'],
                          'shipment': [Shipment, 'shipmentId'],
                          'shipmentdetails': [shipmentDetails, 'orderId'],
                          'orderitems': [OrderItem, 'orderItemId'],
                          'billingdetails': [billingDetails, 'orderId'],
                          'edcshipment': [EdcShipment, 'ordernumber']}

        update_target_class = update_targets[update_target][0]
        update_target_id = getattr(update_target_class, update_targets[update_target][1])

        new_lst = split_list(file, 500)
        for lst in new_lst:
            self.__push_to_db(lst, update_target_id, update_target_class)
            logger.debug(f'Completed {new_lst.index(lst) + 1} of {len(new_lst)}')

        logger.debug(
            f'Successfully inserted {update_target} to Database in {(time.time() - starttime) / 60 :.2f} minutes!')


class SupplierDatabase(Database):
    def __init__(self, connection_type, supplier, supplier_classes):
        super().__init__(connection_type)
        self.supplier = supplier
        self.supplier_classes = supplier_classes

    def get_all_filenames(self):
        SORT_ORDER = ["products", "variants"]
        path = f'{BASE_PATH}/files/{self.supplier}/cleaned/'
        filenames = [os.path.splitext(filename)[0] for filename in os.listdir(path)]

        return [x for x in SORT_ORDER if x in filenames]

    def __add_products(self):
        adapter = Adapter(self.supplier, self.supplier_classes)
        file = adapter.get_products()
        self.insert_in_db(file, update_target='product')

    def __add_stock(self):
        adapter = Adapter(self.supplier, self.supplier_classes)
        file = adapter.get_stock()
        self.insert_in_db(file, update_target='stock')

    def __add_prices(self):
        adapter = Adapter(self.supplier, self.supplier_classes)
        file = adapter.get_prices()
        self.insert_in_db(file, update_target='price')

    def __add_shipment(self, file):
        oap = OrderAdapter()
        file = oap.setup_shipment(file)
        self.insert_in_db(file, update_target='edcshipment')

    def __add_variants(self):
        adapter = Adapter(self.supplier, self.supplier_classes)
        file = adapter.get_variants()
        self.insert_in_db(file, update_target='variant')

    def add_to_db(self, filenames):
        add_methods = {
            'products': self.__add_products,
            'stock': self.__add_stock,
            'price': self.__add_prices,
            'variants': self.__add_variants
        }

        for filename in filenames:
            logger.info(f'Adding {filename.title()}')
            add_methods[filename]()
            logger.info(f'Added {filename.title()}')


class EdcDatabase(SupplierDatabase):
    def __init__(self, connection_type):
        self.supplier = 'edc'
        self.supplier_classes = ALL_EDC_CLASSES
        super().__init__(connection_type,
                         self.supplier,
                         self.supplier_classes)

        self.filenames = super().get_all_filenames()

    def add_to_db(self, *args):
        filenames = self.filenames if args == () else args
        super().add_to_db(filenames)


class BigbuyDatabase(SupplierDatabase):
    def __init__(self, connection_type):
        self.supplier = 'bigbuy'
        self.supplier_classes = ALL_BIGBUY_CLASSES
        super().__init__(connection_type,
                         self.supplier,
                         self.supplier_classes)

        self.filenames = super().get_all_filenames()

    def add_to_db(self, *args):
        filenames = self.filenames if args == () else args
        super().add_to_db(filenames)


class BolDatabase(Database):
    def __init__(self, connection_type):
        super().__init__(connection_type)

    def __push_to_db(self, classes, order_id=None):
        logger.debug('Started Pushing Order to db')
        full_starttime = time.time()

        logger.debug(f"Pushing {classes}")

        for cls in classes:
            bopr = BolAdapter()
            file = bopr.convert_item(classname=cls, order_id=order_id)

            logger.debug(f'Starting on pushing {cls}')

            self.insert_in_db(file, update_target=cls.lower())

        logger.debug(
            f'Successfully pushed {classes} to Database in {(time.time() - full_starttime) / 60 :.2f} minutes!')

    def push_order_to_db(self, order_id):
        classes = ['Order', 'shipmentDetails', 'orderItems', 'billingDetails']
        self.__push_to_db(classes, order_id)

    def push_orders_to_db(self):
        classes = ['Order', 'orderItems']
        self.__push_to_db(classes)

    def push_offers_to_bol(self):
        # get products from EDC db
        with DatabaseSession() as session:
            pass

        # Convert to Offer object and put in db
        # __push_to_db

        # Push Offer objects to bol.com

        # Remove offers that we do not sell any more from bol
        ## API call to bol.com
        ## Update this also in our own db, with a bool "online"
