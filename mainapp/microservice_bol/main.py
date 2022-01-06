import logging.config
from support.database.database_connection import DatabaseSession

from support.database.database import Database, BolDatabase


def main():



    db = BolDatabase(connection_type='merge')
    db.push_orders_to_db()
    db.push_order_to_db(order_id='1043946570')

    db = BolDatabase(connection_type='merge')






if __name__ == '__main__':
    logging.config.fileConfig(fname='logging.config', disable_existing_loggers=False)
    logger = logging.getLogger(__name__)

    main()

#
