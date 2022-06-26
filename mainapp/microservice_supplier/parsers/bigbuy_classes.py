from mainapp.microservice_supplier.parsers.base_classes import Product, Variant, \
    Brand, Measures, Price, Pic, \
    Category, Property, Bulletpoint, Discount

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, TEXT, Float, CHAR, BIGINT, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.orm import relationship

supplier = 'bigbuy'
Base = declarative_base()


class BigbuyProduct(Base, Product):

    __tablename__ = 'products'
    __table_args__ = {'schema': supplier}
    
    def __init__(self, parent):
        super().__init__(parent, supplier)

    supplier = Column(String(50))

    # TODO further split up the percentages in materials (via regex?)
    product_id = Column(Integer, primary_key=True)
    # material = Column(String(255))
    # casecount = Column(Integer)
    # restrictions_germany = Column(String(255))
    artnr = Column(String(255), unique=True)
    title = Column(String(255))
    # description = Column(TEXT)
    # date = Column(Date)
    # modifydate = Column(Date)
    # popularity = Column(Integer)
    # country = Column(String(255))
    # restrictions_platform = Column(String(255))
    # battery_required = Column(Boolean)
    # battery_id = Column(Integer)
    # battery_included = Column(Boolean)
    # battery_quantity = Column(Integer)
    update_date = Column(DateTime)

    measures = relationship("Measures", uselist=False, back_populates="products")
    prices = relationship("Price", uselist=False, back_populates="products")

    variants = relationship("Variant")
    pics = relationship("Pic")

    # brands = relationship("Brand", secondary=brands_products_association)
    # bulletpoints = relationship("Bulletpoint", secondary=bulletpoints_products_association)
    # categories = relationship("Category", secondary=categories_products_association)
    # properties = relationship("Property", secondary=properties_products_association)


class BigbuyVariant(Variant):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class BigbuyBrand(Brand):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class BigbuyPrice(Price):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class BigbuyMeasures(Measures):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class BigbuyPic(Pic):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class BigbuyCategory(Category):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class BigbuyBulletpoint(Bulletpoint):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class BigbuyProperty(Property):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class BigbuyDiscount(Discount):

    def __init__(self, parent):
        super().__init__(parent, supplier)


    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }
