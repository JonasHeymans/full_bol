from mainapp.microservice_supplier.parsers.base_classes import Product, Variant, Brand, Measures, Price, Pic, \
    Category, Property, Bulletpoint, Discount
from mainapp.microservice_supplier.parsers.edc_classes import EdcProduct, EdcVariant, EdcBrand, EdcPrice, EdcMeasures, \
    EdcPic, EdcCategory, EdcBulletpoint, EdcProperty, EdcDiscount

EDC_BASE_URL = 'http://api.edc.nl/'
BB_BASE_URL = 'https://api.bigbuy.eu/'

ALL_EDC_CLASS_NAMES = ['Product', 'Variant', "Price", "Brand", 'Category', 'Measures', 'Property', 'Bulletpoint',
                       'Pic', ]

ALL_EDC_CLASSES = {"Product": EdcProduct,
                   "Variant": EdcVariant,
                   "Brand": EdcBrand,
                   "Price": EdcPrice,
                   "Measures": EdcMeasures,
                   "Pic": EdcPic,
                   "Category": EdcCategory,
                   "Bulletpoint": EdcBulletpoint,
                   "Property": EdcProperty,
                   "Discount": EdcDiscount}

BASE_PATH = 'mainapp/microservice_supplier'
