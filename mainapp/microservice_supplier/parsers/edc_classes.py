from mainapp.microservice_supplier.parsers.base_classes import Product, Variant

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


# class EdcPrice(Price):
#
#     def __init__(self, parent):
#         super().__init__(parent, supplier)
#
#     __mapper_args__ = {
#         'polymorphic_identity': f'{supplier}',
#     }
