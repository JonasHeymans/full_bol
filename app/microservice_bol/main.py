import logging.config
from support.database.database_connection import DatabaseSession

from support.database.database import Database

from app.microservice_bol.retailer.api.api import RetailerAPI

def main():


    api = RetailerAPI(demo=True)
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

    orders = api.orders.get('1043965710')

    db = Database(connection_type='merge')

    with DatabaseSession() as session:
        session.merge(orders)
        logger.debug(f'Pushed {orders} to db')

    print(orders)


if __name__ == '__main__':
    logging.config.fileConfig(fname='logging.config', disable_existing_loggers=False)
    logger = logging.getLogger(__name__)

    main()

#
