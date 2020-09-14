import logging
import time
from sqlalchemy import update


from database_contants import DATABASE_NAME
from database_connection import DatabaseSession
from microservice_bol.parsers.bol_parser import Base


logger = logging.getLogger('microservice_bol.database')

class Database:
    def __init__(self):
        self.db_name = DATABASE_NAME


    def __start_db_session(self):
        Base.metadata.create_all(DatabaseSession().engine)

    def fill_db(self,file):
        with DatabaseSession() as session:
            for x in file:
                session.add(x)
                logger.debug(f'Pushed {x} to db')


    def merge_db(self, file):
        with DatabaseSession() as session:
            for x in file:
                session.merge(x)
                logger.debug(f'Pushed {x} to db')

    def update_db(self, file,table,product_id,dict):
        with DatabaseSession() as session:
            for x in file:
                session.query(table).filter(table.product_id == product_id).update(dict)
                logger.debug(f'Pushed {x} to db')


    def test(self):
        self.__start_db_session()