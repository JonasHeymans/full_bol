import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

logger = logging.getLogger('microservice_edc_pull.database_connection')

from database_contants import *

class DatabaseSession:
    def __init__(self):
        self.connection = None
        self.host = DATABASE_HOST
        self.password = DATABASE_PASSWORD
        self.user = DATABASE_USER
        self.database = DATABASE_NAME
        self.starttime_connection = time.time()
        self.engine = create_engine(f'mysql+mysqlconnector://{self.user}:{self.password}@{self.host}/'
                                    f'{self.database}',echo=False)

    def __enter__(self):

        session = sessionmaker(bind=self.engine)
        logger.debug('DatabaseSession initiated.')
        self.session = session()

        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.close()
        logger.debug(f'DatabaseSession closed. Total connection time: {time.time() - self.starttime_connection :.2f} seconds')


