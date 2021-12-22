import logging.config

from app.microservice_bol.retailer.api.api import RetailerAPI


def main():
    api = RetailerAPI()
    api.login()

    bp = [ {
      "quantity" : 1,
      "unitPrice" : 9.99
    }, {
      "quantity" : 6,
      "unitPrice" : 8.99
    }, {
      "quantity" : 12,
      "unitPrice" : 7.99
    } ]
    orders = api.offers.create_offer('0045496420253', bp, 8)

    print(vars(orders))


if __name__ == '__main__':
    logging.config.fileConfig(fname='logging.config', disable_existing_loggers=False)
    logger = logging.getLogger(__name__)

    main()

#
