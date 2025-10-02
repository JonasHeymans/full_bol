import json
import csv
import logging
import sys
from datetime import date
from decimal import Decimal

import dateutil.parser

logger = logging.getLogger(__name__)


def _is_str(v):
    if sys.version_info >= (3, 0, 0):
        string_types = str,
    else:
        string_types = str,  # I replaced 'basestring' here by 'str' https://docs.python.org/3.0/whatsnew/3.0.html.
        # Might give unexpected behavior, we'll see
        logger.warning('_is_str \"else\" clause reached')
    return isinstance(v, string_types)


def parse_json(content):
    return json.loads(content, parse_float=Decimal)


def parse_csv(content):
    lst = [x for x in csv.reader(content.splitlines(), delimiter=',')]
    keys = lst[0]
    lst = lst[1:]

    return {'offers': [dict(zip(keys, l)) for l in lst]}


class Field(object):
    def parse(self, api, raw_data, instance):
        raise NotImplementedError


class RawField(Field):
    def parse(self, api, raw_data, instance):
        return raw_data


class DecimalField(Field):
    def parse(self, api, raw_data, instance):
        return Decimal(raw_data)


class DateTimeField(Field):
    def parse(self, api, raw_data, instance):
        return dateutil.parser.parse(raw_data)


class DateField(Field):
    def parse(self, api, raw_data, instance):
        parts = raw_data.split("-")
        if len(parts) != 3:
            raise ValueError(raw_data)
        iparts = list(map(int, parts))
        return date(*iparts)


class ModelField(Field):
    def __init__(self, model):
        self.model = model

    def parse(self, api, xml, instance):
        return self.model.parse(api, xml)


class BaseModel(object):
    @classmethod
    def parse(cls, api, content):
        m = cls()

        if _is_str(content):
            if not content.startswith("{"):
                m.raw_data = parse_csv(content)
            else:
                m.raw_data = parse_json(content)
            m.raw_content = content
        else:
            m.raw_content = None
            m.raw_data = content
        return m


class Model(BaseModel):
    @classmethod
    def parse(cls, api, content):
        model = super(Model, cls).parse(api, content)
        for key, value in model.raw_data.items():
            field = getattr(model.Meta, key, RawField())
            setattr(model, key, field.parse(api, value, model))
        return model


class ModelList(list, BaseModel):
    @classmethod
    def parse(cls, api, content):
        ml = super(ModelList, cls).parse(api, content)
        items_key = getattr(ml.Meta, "items_key", None)
        if items_key:
            items = ml.raw_data.get(items_key)
        else:
            items = ml.raw_data
        if items:
            for item in items:
                ml.append(ml.Meta.item_type.parse(api, item))
        return ml


class BillingDetails(Model):
    class Meta:
        pass


class BundlePrice(Model):
    class Meta:
        quantity = DecimalField()
        price = DecimalField()


class BundlePrices(ModelList):
    def __init__(self):
        self.bundle_price = self.Meta.item_type

    class Meta:
        item_type = BundlePrice


class PickUpPoints(Model):
    class Meta:
        pass


class VisibleItem(Model):
    class Meta:
        pass


class Visible(ModelList):
    class Meta:
        item_type = VisibleItem


class ShipmentDetails(Model):
    class Meta:
        pass


class Pricing(Model):
    class Meta:
        bundlePrices = ModelField(BundlePrices)


class Stock(Model):
    class Meta:
        pass


class Fulfilment(Model):
    class Meta:
        pickUpPoints = ModelField(PickUpPoints)


class Store(Model):
    class Meta:
        visible = ModelField(Visible)


class Condition(Model):
    class Meta:
        pass


class NotPublishableReasons(Model):
    class Meta:
        pass


class CustomerDetails(Model):
    class Meta:
        shipmentDetails = ModelField(ShipmentDetails)
        billingDetails = ModelField(BillingDetails)


class Price(Model):
    class Meta:
        PriceAmount = DecimalField()
        BaseQuantity = DecimalField()


class OrderItem(Model):
    class Meta:
        offerPrice = DecimalField()
        transactionFee = DecimalField()
        latestDeliveryDate = DateField()
        expiryDate = DateField()


class OrderItems(ModelList):
    class Meta:
        item_type = OrderItem


class Order(Model):
    class Meta:
        orderPlacedDateTime = DateTimeField()
        customerDetails = ModelField(CustomerDetails)
        orderItems = ModelField(OrderItems)


class Orders(ModelList):
    class Meta:
        item_type = Order
        items_key = "orders"


class Offer(Model):
    class Meta:
        pricing = ModelField(Pricing)
        stock = ModelField(Stock)
        fulfilment = ModelField(Fulfilment)
        store = ModelField(Store)
        condition = ModelField(Condition)
        notPublishableReasons = ModelField(NotPublishableReasons)


class Offers(ModelList):
    class Meta:
        item_type = Offer
        items_key = "offers"


class ShipmentItem(Model):
    class Meta:
        orderDate = DateTimeField()
        latestDeliveryDate = DateTimeField()


class ShipmentItems(ModelList):
    class Meta:
        item_type = ShipmentItem


class Transport(Model):
    class Meta:
        pass


class Shipment(Model):
    class Meta:
        shipmentDate = DateTimeField()
        shipmentItems = ModelField(ShipmentItems)
        transport = ModelField(Transport)


class Shipments(ModelList):
    class Meta:
        item_type = Shipment
        items_key = "shipments"


class ProcessStatus(Model):
    class Meta:
        createTimestamp = DateTimeField()


class ProcessStatuses(ModelList):
    class Meta:
        items_key = "processStatuses"
        item_type = ProcessStatus


class Invoice(Model):
    class Meta:
        pass


class Invoices(ModelList):
    class Meta:
        item_type = Invoice
        items_key = "invoiceListItems"


class InvoiceSpecificationItem(Model):
    class Meta:
        pass


class InvoiceSpecification(ModelList):
    class Meta:
        item_type = InvoiceSpecificationItem
        items_key = "invoiceSpecification"
