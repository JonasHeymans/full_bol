import logging
import math
from datetime import datetime as dt

import numpy as np
from sqlalchemy import Column, Integer, String, Date, TEXT, Float, CHAR, BIGINT, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from support.database.database_connection import DatabaseSession

# TODO: is there something wrong with Categories?
# TODO: Maybe I should give my tables just their class names
# TODO make separate table for measures (1xM)
# TODO brands m2m is still broken
# TODO add try-and except blocks.
# todo does not seem to include remaining and remaining_quantity in variants, update: this todo seems to be fixed?

Base = declarative_base()
schema_name = 'suppliers'

logger = logging.getLogger('microservice_supplier.parser')


class Product(Base):
    __tablename__ = 'products'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent, supplier):
        self.supplier = supplier
        self.product_id = parent['id']
        self.artnr = parent.pop('artnr', None)
        self.ean = parent.pop('ean', None)
        self.update_date = dt.now()
        self.name = parent.pop('name', None)
        self.category = parent.pop('category', None)

    def __repr__(self):
        return f"Product object with product_id '{self.product_id}', artnr '{self.artnr}', enz"

    supplier = Column(String(50))
    product_id = Column(Integer, primary_key=True)
    artnr = Column(String(255), unique=True)
    ean = Column(BIGINT, unique=True)
    update_date = Column(DateTime)
    name = Column(String(255))
    category = Column(String(255))

    variants = relationship("Variant")

    __mapper_args__ = {
        'polymorphic_identity': 'products',
        'polymorphic_on': supplier
    }


class Variant(Base):
    __tablename__ = 'variants'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent, supplier):
        self.supplier = supplier
        self.product_id = parent['product_id']
        self.id = parent.pop('id', None)
        self.artnr = parent['artnr']
        self.ean = parent.pop('ean', None)
        self.purchaseprice = parent.pop('purchaseprice', None)
        self.sellprice = self.__calculate_sellprice(self.purchaseprice)
        self.update_date = dt.now()
        self.stock = parent.pop('stock', None)
        self.update_date_stock = parent.pop('update_date_stock', None)

    def __repr__(self):
        return f"Variant object with product_id '{self.product_id}', artnr '{self.artnr}', enz"

    supplier = Column(String(50))
    id = Column(Integer)
    artnr = Column(String(255), primary_key=True)
    ean = Column(BIGINT)
    stock = Column(Integer)
    update_date_stock = Column(DateTime)
    purchaseprice = Column(Float)
    sellprice = Column(Float)
    update_date = Column(DateTime)

    product_id = Column(Integer, ForeignKey(f'{schema_name}.products.product_id'))

    __mapper_args__ = {
        'polymorphic_identity': 'variants',
        'polymorphic_on': supplier
    }

    def stock_update(self):
        self.update_date_stock = dt.now()

    def __calculate_sellprice(self, purchaseprice):
        # Todo: fix this ugly bugfix properly, I implemented it because we sometimes do not get a b2b price, for example
        # when updating the prices, and we only get a b2c price
        if math.isnan(purchaseprice):
            return np.nan

        bol_commission = 0.15
        profit_margin = 0.1
        tax_percentage = 0.21
        return_percentage = 0.03

        shipping_cost = 9.00


        sell_price = (purchaseprice + shipping_cost + 1) / (1 - bol_commission - profit_margin - tax_percentage- return_percentage)
        rounded_sell_price = math.ceil(sell_price) - 0.01

        return rounded_sell_price

# class Price(Base):
#     __tablename__ = 'prices'
#     __table_args__ = {'schema': schema_name}
#
#     def __init__(self, parent, supplier):
#         self.supplier = supplier
#         self.artnr = parent['artnr']
#         self.product_id = parent.pop('id', None)
#         self.update_date = dt.now()
#
#         self.buy_price = parent['price'].pop('b2b', None)
#
#         self.our_price = self.__calculate_sellprice(self.buy_price)
#
#     def __repr__(self):
#         return f"Price object with artnr '{self.artnr}', b2b '{self.b2b}', enz"
#
#     supplier = Column(String(50))
#     product_id = Column(Integer)
#     subartnr = Column(String(100))
#     update_date = Column(DateTime)
#     init_date = Column(DateTime)
#     buy_price = Column(Float)
#     our_price = Column(Float)
#     b2bsale = Column(Float)
#     artnr = Column(String(255), ForeignKey(f'{schema_name}.products.artnr'), primary_key=True)
#     products = relationship("Product", back_populates="prices")
#
#     # Math seems to be ok, but still edc gives other prices on their site. So use the provided feed instead of calculating it yourself
#     def __calculate_buy_price(self, b2b_price, b2bsale, discount, discount_percentage):
#
#         b2b_price = b2bsale if b2bsale != np.nan else b2b_price
#
#         b2b_price = float(b2b_price)
#
#         if discount.upper() == 'Y':
#             buy_price = b2b_price - (b2b_price * (discount_percentage / 100))
#         elif discount.upper() == 'N':
#             buy_price = b2b_price
#         else:
#             buy_price = 99999999999  # Just a quick and dirty safety measure
#             logger.warning("Error in calculating sellprice: discount is neither Y nor N")
#
#         return buy_price
#
#     def __calculate_sellprice(self, buy_price):
#         # Todo: fix this ugly bugfix properly, I implemented it because we sometimes do not get a b2b price, for example
#         # when updating the prices, and we only get a b2c price
#         if math.isnan(buy_price):
#             return np.nan
#
#         bol_commission = 0.15
#         profit_margin = 0.10
#         shipping_cost = 6.50
#
#         sell_price = (buy_price + shipping_cost + 1) / (1 - bol_commission - profit_margin)
#         rounded_sell_price = math.ceil(sell_price) - 0.01
#
#         return rounded_sell_price
