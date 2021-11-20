from microservice_edc_pull.database.database import Database
from microservice_edc_pull.parsers.converter import Converter
from microservice_edc_pull.libs.edc import EdcClient
from microservice_edc_pull.products.products import AllEdcProduct


from logger.logger import Logger



log = Logger()
log.get_commandline_logger('DEBUG')

# Something is really going wrong with categories in the converter class I think!
# eg1: item: '11128' has double entries in the db (eg: 2x "Drogisterij', 2x 'Massage Olie', also: the programs says that 'Something went very wrong in the convert function!",
# Error is something with nonetype
# TODO check- and change datatypes. Eg; Bool instead of 'Y'/'N'
# TODO check fully blank columns. Eg. artnr and update_date for prices


