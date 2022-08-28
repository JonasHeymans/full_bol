from dotenv import load_dotenv

from mainapp.microservice_supplier.parsers.base_classes import *
# Product, Variant, Brand, Measures, Price, Pic, Category, Property, Bulletpoint, Discount
from mainapp.microservice_supplier.parsers.edc_classes import EdcProduct, EdcVariant
from mainapp.microservice_supplier.parsers.bigbuy_classes import BigbuyProduct, BigbuyVariant

load_dotenv()

EDC_BASE_URL = 'http://api.edc.nl/'
BB_BASE_URL = 'https://api.bigbuy.eu/'

ALL_EDC_CLASS_NAMES = ['Product', 'Variant', "Price", "Brand", 'Category', 'Measures', 'Property', 'Bulletpoint',
                       'Pic']

ALL_EDC_CLASSES = {"Product": EdcProduct,
                   "Variant": EdcVariant}

ALL_BIGBUY_CLASSES = {"Product": BigbuyProduct,
                      "Variant": BigbuyVariant}

BASE_PATH = 'mainapp/microservice_supplier'
