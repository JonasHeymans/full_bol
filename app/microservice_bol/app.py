import logging
import logging.config

from microservice_bol.retailer.api.api import RetailerAPI
from microservice_bol.retailer.models.models import BundlePrices,BundlePrice
from microservice_bol.constants.constants import CancellationReasonCode

def main():

    api = RetailerAPI()
    api.login()

    orders = api.orders.list()

    for x in orders:
        print(x)



if __name__ == '__main__':
    logging.config.fileConfig(fname = 'logging.config', disable_existing_loggers=False)
    logger = logging.getLogger(__name__)

    main()

# TODO: implement logging
# TODO: Expand program: add coverage for Offers (and other methods?) so we can update the price, delete offers,..