from sqlalchemy.ext.declarative import declarative_base

# I probably do stupid
Base = declarative_base()


class Offer(Base):

    def __init__(self):
        pass

    def __repr__(self):
        pass


class Order(Base):

    def __init__(self):
        pass

    def __repr__(self):
        pass

    def add_trackingcode(self):
        pass


class Customer(Base):

    def __init__(self, parent):
        self.firstname = parent['firstname']


    def __repr__(self):
        pass