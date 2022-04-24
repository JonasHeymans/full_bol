from sqlalchemy import Column, String

from mainapp.microservice_supplier.parsers.base_classes import Product, Variant, \
    Brand, Measures, Price, Pic, \
    Category, Property, Bulletpoint, Discount

supplier_name = 'edc'


class EdcProduct(Product):

    def __init__(self, parent):
        super().__init__(parent, supplier_name)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier_name}',
    }


class EdcVariant(Variant):

    def __init__(self, parent):
        super().__init__(parent, supplier_name)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier_name}',
    }


class EdcBrand(Brand):

    def __init__(self, parent):
        super().__init__(parent, supplier_name)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier_name}',
    }


class EdcPrice(Price):

    def __init__(self, parent):
        super().__init__(parent, supplier_name)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier_name}',
    }


class EdcMeasures(Measures):

    def __init__(self, parent):
        super().__init__(parent, supplier_name)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier_name}',
    }


class EdcPic(Pic):

    def __init__(self, parent):
        super().__init__(parent, supplier_name)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier_name}',
    }


class EdcCategory(Category):

    def __init__(self, parent):
        super().__init__(parent, supplier_name)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier_name}',
    }


class EdcBulletpoint(Bulletpoint):

    def __init__(self, parent):
        super().__init__(parent, supplier_name)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier_name}',
    }


class EdcProperty(Property):

    def __init__(self, parent):
        super().__init__(parent, supplier_name)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier_name}',
    }


class EdcDiscount(Discount):

    def __init__(self, parent):
        super().__init__(parent, supplier_name)


    __mapper_args__ = {
        'polymorphic_identity': f'{supplier_name}',
    }
