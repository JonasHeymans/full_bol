
from microservice_edc_pull.database.database import Database
from microservice_edc_pull.parsers.converter import Converter
from microservice_edc_pull.libs.edc import EDC_Client
from microservice_edc_pull.products.products import All_EDC_Product


from microservice_edc_pull.logger.logger import Logger




Logger().get_commandline_logger('info')


# Something is really going wrong with categories in the converter class I think!
# eg1: item: '11128' has double entries in the db (eg: 2x "Drogisterij', 2x 'Massage Olie', also: the programs says that 'Something went very wrong in the convert function!",
# Error is something with nonetype


Database.update_prices()
