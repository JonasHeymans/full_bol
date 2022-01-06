import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema
import time
from decouple import config


logger = logging.getLogger(__name__)


class DatabaseSession:
    def __init__(self):
        self.connection = None
        self.DATABASE_URL = config('DATABASE_URL')

        self.starttime_connection = time.time()
        self.engine = create_engine(self.DATABASE_URL,echo=False)




    def __enter__(self):

        session = sessionmaker(bind=self.engine)
        logger.debug('DatabaseSession initiated.')
        self.session = session()

        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.close()
        logger.debug(f'DatabaseSession closed. Total connection time: {(time.time() - self.starttime_connection)/60 :.2f} minutes')





