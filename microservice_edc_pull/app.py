
from microservice_edc_pull.database.database import Database
from microservice_edc_pull.parsers.converter import Converter
from microservice_edc_pull.libs.edc import EdcClient
from microservice_edc_pull.products.products import AllEdcProduct


from microservice_edc_pull.logger.logger import Logger



log = Logger()
log.get_commandline_logger('DEBUG')

# Something is really going wrong with categories in the converter class I think!
# eg1: item: '11128' has double entries in the db (eg: 2x "Drogisterij', 2x 'Massage Olie', also: the programs says that 'Something went very wrong in the convert function!",
# Error is something with nonetype

edc = EdcClient()
edc.download_prices('update')

pd = Database()
pd.push_prices_to_db()
