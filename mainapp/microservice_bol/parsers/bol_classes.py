from sqlalchemy import Column, Integer, String, TEXT, Boolean, DateTime, Date, ForeignKey, BIGINT, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from mainapp.microservice_bol.constants.constants import TimeFrameType, DistributionParty, Salutation, ConditionName, \
    FulfilmentMethod, DeliveryCode

Base = declarative_base()
schema_name = 'bol'


class Item:
    def extract(self, to_extract, top_level=None):
        try:
            if top_level:
                in_parent = hasattr(self.parent, f'{top_level}')
                if in_parent:
                    child = getattr(self.parent, top_level)

                    return child[f'{to_extract}']
                else:
                    getattr(self.parent, to_extract)
            else:
                return self.parent[f'{to_extract}']
        except:
            return None

    # todo: implement these validations
    def validate_zipcode(self):
        self.extract('zipCode')

    def validate_email(self):
        self.extract('email')

    def validate_language(self):
        language = self.extract('email')
        if language in ['nl', 'fr', 'nl-BE', 'fr-BE']:
            return language
        else:
            raise KeyError('Wrong Language')


class Order(Base, Item):
    __tablename__ = 'orders'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent):
        super().__init__()
        self.orderId = parent.orderId
        self.orderPlacedDateTime = parent.orderPlacedDateTime

    def __repr__(self):
        return f"Order object"

    orderId = Column(String(32), primary_key=True)
    orderPlacedDateTime = Column(DateTime)

    shipment = relationship("Shipment", back_populates="order", uselist=False)

    orderitem = relationship("OrderItem", back_populates="order", uselist=False)

    shipmentdetails = relationship("shipmentDetails", back_populates="order", uselist=False)
    billingdetails = relationship("billingDetails", back_populates="order", uselist=False)


class OrderItem(Base, Item):
    __tablename__ = 'orderitems'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.orderItemId = parent.orderItemId

        self.cancellationRequest = self.extract('cancellationRequest', 'product')
        self.ean = self.extract('ean', 'product')
        self.title = self.extract('title', 'product')
        self.offerId = self.extract('offerId', 'offer')
        self.reference = self.extract('reference', 'offer')
        self.method = self.extract('method', 'fulfilment')
        self.distributionParty = self.extract('distributionParty', 'fulfilment')
        self.latestDeliveryDate = self.extract('latestDeliveryDate', 'fulfilment')
        self.exactDeliveryDate = self.extract('exactDeliveryDate', 'fulfilment')
        self.expiryDate = self.extract('expiryDate', 'fulfilment')
        self.timeFrameType = self.extract('timeFrameType', 'fulfilment')
        self.quantity = parent.quantity
        self.quantityCancelled = parent.quantityCancelled
        self.quantityShipped = parent.quantityShipped

        self.orderId = parent.orderId

    orderItemId = Column(String(32), primary_key=True)

    cancellationRequest = Column(Boolean)
    ean = Column(BIGINT)
    title = Column(String(256))
    offerId = Column(String(256))
    reference = Column(String(256))
    method = Column(String(256))
    distributionParty = Column(Enum(DistributionParty))
    latestDeliveryDate = Column(Date)
    exactDeliveryDate = Column(Date)
    expiryDate = Column(Date)
    timeFrameType = Column(Enum(TimeFrameType))
    quantity = Column(Integer)
    quantityCancelled = Column(Integer)
    quantityShipped = Column(Integer)

    orderId = Column(String(32), ForeignKey(f'{schema_name}.orders.orderId'))
    order = relationship("Order", back_populates="orderitem")


class Shipment(Base, Item):
    __tablename__ = 'shipments'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.shipmentId = parent.shipmentId

        self.orderId = parent.orderId

    def __repr__(self):
        return f"Shipment object"

    def add_tracking_code(self):
        pass

    shipmentId = Column(Integer, primary_key=True)
    shipmentDateTime = Column(DateTime)
    shipmentReference = Column(String(32))
    pickupPoint = Column(Boolean)

    shipment_date = Column(DateTime)
    shipment_reference = Column(String(32))
    customer_details = Column(TEXT)

    billing_details = Column(TEXT)
    detail_fetched = Column(Boolean, default=False)

    orderId = Column(String(32), ForeignKey(f'{schema_name}.orders.orderId'))
    order = relationship("Order", back_populates="shipment")


# class Seller(TimeStampedModel):
#     first_name = models.CharField(_("Seller First Name"), max_length=255, blank=False, null=False)
#     last_name = models.CharField(_("Seller Last Name"), max_length=255, blank=False, null=False)
#     shop_name = models.CharField(_("Shop Name"), max_length=255, blank=False, null=False)
#     client_id = models.CharField(_("Client ID"), max_length=100, blank=False, null=False)
#     client_secret = models.CharField(_("Client Secret"), max_length=255, blank=False, null=False)
#     last_synced_at = models.DateTimeField(_("Last synced at"), blank=True, null=True)
#
#     def __str__(self):
#         return '{} {}'.format(self.first_name, self.last_name)

class shipmentDetails(Base, Item):
    __tablename__ = 'shipmentdetails'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.orderId = self.extract('orderId')

        self.pickupPointName = self.extract('pickupPointName')
        self.salutation = self.extract('salutation')
        self.firstName = self.extract('firstName')
        self.surname = self.extract('surname')
        self.streetName = self.extract('streetName')
        self.houseNumber = self.extract('houseNumber')
        self.houseNumberExtension = self.extract('houseNumberExtension')
        self.extraAddressInformation = self.extract('extraAddressInformation')
        self.zipCode = self.validate_zipcode()
        self.city = self.extract('city')
        self.countryCode = self.extract('countryCode')
        self.email = self.validate_email()
        self.company = self.extract('company')
        self.deliveryPhoneNumber = self.extract('deliveryPhoneNumber')
        self.language = self.extract('language')

    orderId = Column(String(32), ForeignKey(f'{schema_name}.orders.orderId'), primary_key=True)
    order = relationship("Order", back_populates="shipmentdetails")

    pickupPointName = Column(String(256))
    salutation = Column(Enum(Salutation))
    firstName = Column(String(256))
    surname = Column(String(256))
    streetName = Column(String(256))
    houseNumber = Column(Integer)
    houseNumberExtension = Column(String(3))
    extraAddressInformation = Column(String(256))
    zipCode = Column(String(256))
    city = Column(String(256))
    countryCode = Column(String(3))
    email = Column(String(256))
    company = Column(String(256))
    deliveryPhoneNumber = Column(Integer)
    language = Column(String(4))  # Should this be an enum? Because it fails if I try to implement.


class ShipmentItem(Base, Item):
    __tablename__ = 'shipmentitems'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent):
        super().__init__()

        self.shipmentId = parent.shipmentId

    # shipment = models.ForeignKey(Shipment, _("Shipment"), blank=False, null=False)
    # order = models.ForeignKey(Order, _("Order"), blank=False, null=False)
    # order_item = models.ForeignKey(OrderItem, _("Order Item"), blank=False, null=False)

    shipmentId = Column(Integer, primary_key=True, autoincrement=True)

    shipmentDateTime = Column(DateTime)
    shipmentReference = Column(String(256))

    def __str__(self):
        pass


# class Transport(TimeStampedModel):
#     shipment = models.ForeignKey(Shipment, _("Shipment"), blank=False, null=False)
#     transport_id = models.CharField(_("Transport ID"), primary_key=True, max_length=32, blank=False, null=False)
#     transporter_code = models.CharField(_("Transporter Code"), max_length=32, blank=False, null=False)
#     track_and_trace = models.CharField(_("Track and Trace"), max_length=32, blank=False, null=False)
#
#     # Shipping label could be a ForeignKey but for simplicity it is assumed part of the Transport
#     shipping_label_id = models.CharField(_("Shipping Label ID"), max_length=32, blank=True, null=True)
#     shipping_label_code = models.CharField(_("Shipping Label Code"), max_length=32, blank=True, null=True)
#
#     def __str__(self):
#         return '{}'.format(self.transport_id)

class billingDetails(Base, Item):
    __tablename__ = 'billingdetails'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.orderId = self.extract('orderId')

        self.salutation = self.extract('salutation')
        self.firstName = self.extract('firstName')
        self.surname = self.extract('surname')
        self.streetName = self.extract('streetName')
        self.houseNumber = self.extract('houseNumber')
        self.houseNumberExtension = self.extract('houseNumberExtension')
        self.extraAddressInformation = self.extract('extraAddressInformation')
        self.zipCode = self.validate_zipcode()
        self.city = self.extract('city')
        self.countryCode = self.extract('countryCode')
        self.email = self.validate_email()
        self.company = self.extract('company')

        self.vatNumber = self.extract('vatNumber')
        self.kvkNumber = self.extract('kvkNumber')
        self.orderReference = self.extract('orderReference')

    orderId = Column(String(32), ForeignKey(f'{schema_name}.orders.orderId'), primary_key=True)
    order = relationship("Order", back_populates="billingdetails")

    salutation = Column(Enum(Salutation))
    firstName = Column(String(256))
    surname = Column(String(256))
    streetName = Column(String(256))
    houseNumber = Column(Integer)
    houseNumberExtension = Column(String(3))
    extraAddressInformation = Column(String(256))
    zipCode = Column(String(256))
    city = Column(String(256))
    countryCode = Column(String(3))
    email = Column(String(256))
    company = Column(String(256))

    vatNumber = Column(String(50))
    kvkNumber = Column(String(50))
    orderReference = Column(String(256))


class Offer(Base, Item):
    __tablename__ = 'offers'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.ean = self.extract('ean')
        self.condition = self.extract('condition')
        self.reference = self.extract('reference')
        self.onHoldByRetailer = self.extract('onHoldByRetailer')
        self.stockamount = self.extract('stockamount')
        self.managedByRetailer = True
        self.fulfilmentmethod = self.extract('fulfilmentmethod')
        self.deliverycode = self.extract('deliverycode')

    ean = Column(BIGINT, primary_key=True)
    condition = Column(Enum(ConditionName))
    reference = Column(String(10))
    onHoldByRetailer = Column(Boolean)
    stockamount = Column(Integer)
    managedByRetailer = Column(Boolean)
    fulfilmentmethod = Column(Enum(FulfilmentMethod))
    deliverycode = Column(Enum(DeliveryCode))

    prices = relationship("Price", back_populates='offer')


class Price(Base, Item):
    __tablename__ = 'prices'
    __table_args__ = {'schema': schema_name}

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.quantity = self.extract('quantity')
        self.unitPrice = self.extract('unitPrice')

    id = Column(Integer, primary_key=True, autoincrement=True)

    quantity = Column(Integer)
    unitPrice = Column(Integer)

    offer_id = Column(BIGINT, ForeignKey(f'{schema_name}.offers.ean'))
    offer = relationship("Offer", back_populates="prices")


class fulfilment():
    pass


class product():
    pass
