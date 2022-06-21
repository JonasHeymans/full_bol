from mainapp.microservice_supplier.parsers.base_classes import Product, Variant, \
    Brand, Measures, Price, Pic, \
    Category, Property, Bulletpoint, Discount

supplier = 'edc'


class EdcProduct(Product):
    
    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class EdcVariant(Variant):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class EdcBrand(Brand):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class EdcPrice(Price):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class EdcMeasures(Measures):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class EdcPic(Pic):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class EdcCategory(Category):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class EdcBulletpoint(Bulletpoint):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class EdcProperty(Property):

    def __init__(self, parent):
        super().__init__(parent, supplier)

    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }


class EdcDiscount(Discount):

    def __init__(self, parent):
        super().__init__(parent, supplier)


    __mapper_args__ = {
        'polymorphic_identity': f'{supplier}',
    }
