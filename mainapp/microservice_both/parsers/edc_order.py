from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
schema_name = 'edc_order'


class EdcOrder:
    pass


class EdcShipment(Base):
    __tablename__ = 'edcshipments'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent):
        self.ordernumber = parent['ordernumber']
        self.own_ordernumber = parent['own_ordernumber']
        self.new_ordernumber = parent['new_ordernumber']
        self.tracktrace = parent['tracktrace']
        self.shipper = parent['shipper']
        self.status = parent['status']
        self.send_to_bol = False

    ordernumber = Column(String(50), primary_key=True)
    own_ordernumber = Column(String(50))
    new_ordernumber = Column(String(50))
    tracktrace = Column(String(50))
    shipper = Column(String(50))
    status = Column(String(50))
    send_to_bol = Column(Boolean)


# class EdcOrder(Base):
#     __tablename__ = 'edcorders'
#     __table_args__ = {'schema': schema_name}
#
#     def __init__(self, parent):
#         pass