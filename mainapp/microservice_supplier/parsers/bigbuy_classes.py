from mainapp.microservice_supplier.parsers.base_classes import Product, Variant

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


# class BigbuyPrice(Price):
#
#     def __init__(self, parent):
#         super().__init__(parent, supplier)
#
#     __mapper_args__ = {
#         'polymorphic_identity': f'{supplier}',
#     }
