from mainapp.microservice_supplier.parsers.base_classes import *
# Product, Variant, Brand, Measures, Price, Pic, Category, Property, Bulletpoint, Discount
from mainapp.microservice_supplier.parsers.edc_classes import EdcProduct, EdcVariant, EdcBrand, EdcPrice, EdcMeasures, \
    EdcPic, EdcCategory, EdcBulletpoint, EdcProperty, EdcDiscount
from mainapp.microservice_supplier.parsers.bigbuy_classes import BigbuyProduct, BigbuyVariant, BigbuyBrand, BigbuyPrice, BigbuyMeasures, \
    BigbuyPic, BigbuyCategory, BigbuyBulletpoint, BigbuyProperty, BigbuyDiscount

EDC_BASE_URL = 'http://api.edc.nl/'
BB_BASE_URL = 'https://api.sandbox.bigbuy.eu/'

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

ALL_BIGBUY_CLASSES = {"Product": BigbuyProduct,
                   "Variant": BigbuyVariant,
                   "Brand": BigbuyBrand,
                   "Price": BigbuyPrice,
                   "Measures": BigbuyMeasures,
                   "Pic": BigbuyPic,
                   "Category": BigbuyCategory,
                   "Bulletpoint": BigbuyBulletpoint,
                   "Property": BigbuyProperty,
                   "Discount": BigbuyDiscount}

BASE_PATH = 'mainapp/microservice_supplier'


