from mainapp.microservice_supplier.parsers.base_classes import Product, Variant, \
    Brand, Measures, Price, Pic, \
    Category, Property, Bulletpoint, Discount

supplier = 'bigbuy'


class BigbuyProduct(Product):
    
    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


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
