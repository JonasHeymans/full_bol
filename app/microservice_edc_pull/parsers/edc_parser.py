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


logger = logging.getLogger('microservice_edc_pull.parser')

Base = declarative_base()

brands_products_association = Table('brands_products', Base.metadata,
                                    Column('products_id', Integer, ForeignKey('products.product_id')),
                                    Column('brands_id', Integer, ForeignKey('brands.brand_id')))


#
# categories_products_association = Table('categories_products', Base.metadata,
#                                 Column('products_id', Integer, ForeignKey('products.id')),
#                                 Column('categories_id', Integer, ForeignKey('categories.product_id')))

# properties_products_association = Table('properties_products', Base.metadata,
#                                 Column('products_id', Integer, ForeignKey('products.id')),
#                                 Column('properties_id', Integer, ForeignKey('properties.product_id')))
#
# bulletpoints_products_association = Table('bulletpoints_products', Base.metadata,
#                                 Column('products_id', Integer, ForeignKey('products.id')),
#                                 Column('bulletpoints_id', Integer, ForeignKey('bulletpoints.product_id')))
#


class Product(Base):
    __tablename__ = 'products'

    def __init__(self, parent):
        self.product_id = parent['id']
        self.artnr = parent.pop('artnr', None)
        self.title = parent.pop('title', None)
        self.description = parent.pop('description', None)
        self.date = parent.pop('date', None)
        self.modifydate = parent.pop('modifydate', None)
        self.material = parent.pop('material', None)
        self.popularity = parent.pop('popularity', None)
        self.country = parent.pop('country', None)
        self.restrictions_platform = parent['restrictions'].pop('platform', None)
        self.battery_required = False if not isinstance(parent['battery'], list) else True
        self.battery_id = None if self.battery_required == False else parent['battery'][0].pop('id', None)
        self.battery_included = None if self.battery_required == False else (
            True if parent['battery'][0].pop('included', None) == 'Y' else False)
        self.battery_quantity = None if self.battery_required == False else parent['battery'][0].pop('quantity', None)
        self.casecount = parent.pop('casecount', None)
        self.restrictions_germany = parent['restrictions'].pop('germany', None)
        self.update_date = dt.now()

    def __repr__(self):
        return f"Product object with product_id '{self.product_id}', artnr '{self.artnr}', title '{self.title}', enz"

    # TODO further split up the percentages in materials (via regex?)
    product_id = Column(Integer, primary_key=True)
    material = Column(String(255))
    casecount = Column(Integer)
    restrictions_germany = Column(String(255))
    artnr = Column(String(255), unique=True)
    title = Column(String(255))
    description = Column(TEXT)
    date = Column(Date)
    modifydate = Column(Date)
    popularity = Column(Integer)
    country = Column(String(255))
    restrictions_platform = Column(String(255))
    battery_required = Column(Boolean)
    battery_id = Column(Integer)
    battery_included = Column(Boolean)
    battery_quantity = Column(Integer)
    update_date = Column(DateTime)

    measures = relationship("Measures", uselist=False, back_populates="products")
    prices = relationship("Price", uselist=False, back_populates="products")

    variants = relationship("Variant")
    pics = relationship("Pic")

    brands = relationship("Brand", secondary=brands_products_association)
    # bulletpoints = relationship("Bulletpoint", secondary=bulletpoints_products_association)
    # # categories = relationship("Category", secondary=categories_products_association)
    # # properties = relationship("Property", secondary=properties_products_association)


class Variant(Base):
    __tablename__ = 'variants'

    def __init__(self, parent):
        self.product_id = parent['product_id']
        self.variant_id = parent.pop('id', None)
        self.type = parent.pop('type', None)
        self.subartnr = parent['subartnr']
        self.ean = parent.pop('ean', None)
        self.stock = parent.pop('stock', None)
        self.stockestimate = parent.pop('stockestimate', None)
        self.weeknr = parent.pop('weeknr', None)
        self.nova = parent.pop('nova', None)
        self.title = parent.pop('title', None)
        self.remaining = parent.pop('remaining', None)
        self.remaining_quantity = parent.pop('remaining_quantity', None)

    def __repr__(self):
        return f"Variant object with product_id '{self.product_id}', subartnr '{self.subartnr}', type '{self.type}', enz"

    variant_id = Column(Integer, )
    type = Column(String(255))
    subartnr = Column(String(255), primary_key=True)
    ean = Column(BIGINT)
    stock = Column(String(255))
    stockestimate = Column(Integer)
    weeknr = Column(Integer)
    nova = Column(TEXT)  # todo, check which is the correct filetype
    title = Column(String(255))
    remaining = Column(CHAR)
    remaining_quantity = Column(Integer)
    update_date_stock = Column(DateTime)

    product_id = Column(Integer, ForeignKey('products.product_id'))

    def stock_update(self):
        self.update_date_stock = dt.now()

    def extract_product(self):
        # todo: am I doing something dangerous here by saying that artnr == subartnr?
        p = Product({'id': self.product_id,
                     'artnr': self.subartnr,
                     'restrictions': {},
                     'battery': {}})
        return p


class Brand(Base):
    __tablename__ = 'brands'

    def __init__(self, parent):
        self.product_id = parent['id']
        self.brand_id = parent['brand'].pop('id', None)
        self.title = parent['brand'].pop('title', None)

    def __repr__(self):
        return f"Brand object with product_id '{self.product_id}', brand_id '{self.brand_id}' and title '{self.title}'"

    brand_id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    title = Column(String(255))


class Price(Base):
    __tablename__ = 'prices'

    def __init__(self, parent):
        self.artnr = parent['artnr']
        self.product_id = parent.pop('id', None)
        self.discount = parent['price'].pop('discount', None)
        self.discount_percentage = 0  # todo, removed    just to make it run faster and I don't currently use this method
        self.update_date = dt.now()
        self.b2bsale = parent['price'].pop('b2bsale', None)

    def __repr__(self):
        return f"Price object with artnr '{self.artnr}', currency '{self.currency}', b2b '{self.b2b}', enz"

    product_id = Column(Integer)
    subartnr = Column(String(100))
    update_date = Column(DateTime)
    init_date = Column(DateTime)
    currency = Column(String(20))
    b2b = Column(Float)
    b2c = Column(Float)
    vatnl = Column(Float)
    vatde = Column(Float)
    vatfr = Column(Float)
    vatuk = Column(Float)
    discount = Column(CHAR)
    discount_percentage = Column(Integer)
    brand_id = Column(Integer)
    buy_price = Column(Float)
    our_price = Column(Float)
    b2bsale = Column(Float)

    artnr = Column(String(255), ForeignKey('products.artnr'), primary_key=True)
    products = relationship("Product", back_populates="prices")

    def add_init_attibutes(self, parent):

        self.currency = parent['price'].pop('currency', None)
        self.vatnl = float(parent['price'].pop('vatnl', np.nan))
        self.vatde = float(parent['price'].pop('vatde', np.nan))
        self.vatfr = float(parent['price'].pop('vatfr', np.nan))
        self.vatuk = float(parent['price'].pop('vatuk', np.nan))

        self.init_date = dt.now()
        self.add_setup_attibutes(parent)
        self.add_update_attibutes(parent)

    def add_setup_attibutes(self, parent):
        self.subartnr = parent.pop('subartnr', None)

    def add_update_attibutes(self, parent):
        self.b2b = float(parent['price'].pop('b2b', np.nan))
        self.b2c = float(parent['price'].pop('b2c', np.nan))
        self.brand_id = parent['brand'].pop('id', None)
        # self.__get_discount_percentage(self.brand_id )

        self.buy_price = self.__calculate_buy_price(self.b2b, self.discount, self.discount_percentage)
        self.our_price = self.__calculate_sellprice(self.b2b)
        # todo: change the argument here back to self.buy_price when I find out why we do not get the correct discounts

    # Math seems to be ok, but still edc gives other prices on their site. So use the provided feed instead of calculating it yourself
    def __calculate_buy_price(self, b2b_price, discount, discount_percentage):
        b2b_price = float(b2b_price)

        if discount.upper() == 'Y':
            buy_price = b2b_price - (b2b_price * (discount_percentage / 100))
        elif discount.upper() == 'N':
            buy_price = b2b_price
        else:
            buy_price = 99999999999  # Just a quick and dirty safety measure
            logger.warning("Error in calculating sellprice: discount is neither Y nor N")

        return buy_price

    def __calculate_sellprice(self, buy_price):
        # Todo: fix this ugly bugfix properly, I implemented it because we sometimes do not get a b2b price, for example
        # when updating the prices, and we only get a b2c price
        if math.isnan(buy_price):
            return np.nan

        bol_commission = 0.15
        profit_margin = 0.15
        shipping_cost = 6.50

        sell_price = (buy_price + shipping_cost + 1) / (1- bol_commission - profit_margin)
        rounded_sell_price = math.ceil(sell_price) - 0.01

        return rounded_sell_price

    # Todo: this is really slow, constantly making a connection to the db is not smart. Need to improve this.
    def __get_discount_percentage(self, brand_id):
        Base.metadata.create_all(DatabaseSession().engine)
        with DatabaseSession() as session:
            discount_object = session.query(Discount).get(brand_id)
            try:
                return discount_object.discount
            except Exception:
                logger.debug(f'Error on getting discount for product with brand_id {brand_id}')

    def extract_product(self):
        p = Product({'id': self.product_id,
                     'artnr': self.subartnr,
                     'restrictions': {},
                     'battery': {}})
        return p

    def extract_variant(self):
        v = Variant({'product_id': self.product_id,
                     'subartnr': self.subartnr})
        return v


class Measures(Base):
    __tablename__ = 'measures'

    def __init__(self, parent):
        if parent['measures'] and parent['id'] != None:
            self.product_id = parent['id']
            self.insertiondepth = parent['measures'].pop('insertiondepth', 0)
            self.length = parent['measures'].pop('length', None)
            self.maxdiameter = parent['measures'].pop('maxdiameter', None)
            self.weight = parent['measures'].pop('weight', None)
            self.packing = parent['measures'].pop('packing', None)

    def __repr__(self):
        return f"Measures object with product_id '{self.product_id}', insertiondepth '{self.insertiondepth}', length '{self.length}', enz"

    product_id = Column(Integer, ForeignKey('products.product_id'), primary_key=True)
    maxdiameter = Column(Float)
    insertiondepth = Column(Float)
    weight = Column(Integer)
    packing = Column(String(255))
    length = Column(Float)

    products = relationship("Product", back_populates="measures")


# TODO can't I here not also include the product_id?
class Pic(Base):
    __tablename__ = 'pics'

    def __init__(self, parent):
        self.product_id = parent['product_id']
        self.artnr = parent['id']
        self.pic = parent['pic']

    def __repr__(self):
        return f"Pic object with artnr '{self.artnr}' and pic '{self.pic}'"

    pic = Column(String(255), primary_key=True)
    artnr = Column(String(255))

    product_id = Column(Integer, ForeignKey('products.product_id'))


class Category(Base):
    __tablename__ = 'categories'

    def __init__(self, parent):
        self.product_id = parent['product_id']
        self.category_id = parent['id']
        self.title = parent['title']

    product_id = Column(Integer)
    category_id = Column(Integer, primary_key=True)
    title = Column(String(255))

    def __repr__(self):
        return f"Category object with product_id '{self.product_id}', category_id '{self.category_id}' and title '{self.title}'"


class Bulletpoint(Base):
    __tablename__ = 'bulletpoints'

    def __init__(self, parent):
        self.product_id = parent['product_id']
        self.bp = parent['bp']

    def __repr__(self):
        return f"Bulletpoint object with product_id '{self.product_id}' and bulletpoint '{self.bp}'"

    bp = Column(String(255), primary_key=True)
    product_id = Column(Integer)


class Property(Base):
    __tablename__ = 'properties'

    # Note that valueid is not necessarily equal to value_id. Why, I don't know/
    # TODO Properties is still way too confusing, i don't really understand what all the relationships are.

    def __init__(self, parent):
        self.product_id = parent['product_id']
        self.propid = parent['propid']
        self.property = parent['property']
        self.valueid = parent['valueid']
        self.value = parent['value']

        try:
            self.value_id = parent['id']
            self.title = parent['title']
        except KeyError as e:
            if str(e) == "'id'":
                self.unit = parent['unit']
                self.magnitude = parent['magnitude']
            else:
                raise Exception

    def __repr__(self):
        return f"Property object with product_id '{self.product_id}' and propid '{self.propid}'"

    propid = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    property = Column(String(255))
    valueid = Column(Integer)
    value = Column(String(255))
    value_id = Column(Integer)
    title = Column(String(255))
    unit = Column(String(255))
    magnitude = Column(Integer)


# Still none of the MXM's works

class Discount(Base):
    __tablename__ = 'discounts'

    def __init__(self, parent):
        self.brand_id = parent[0]
        self.brandname = parent[1]
        self.discount = parent[2]

    def __repr__(self):
        return f"Discount object with brand_id '{self.brand_id}', brandname '{self.brandname}' and discount '{self.discount}'"

    brand_id = Column(Integer, primary_key=True)
    brandname = Column(String(255))
    discount = Column(Integer)
