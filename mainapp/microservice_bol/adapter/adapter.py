import logging

from mainapp.microservice_bol.parsers.bol_classes import Order, shipmentDetails, OrderItem, billingDetails
from mainapp.microservice_bol.retailer.api.api import RetailerAPI

logger = logging.getLogger(__name__)


class BolAdapter:
    def __init__(self):
        self.api = RetailerAPI()

    def convert_item(self, classname: str, order_id=None):
        self.api.login()

        if order_id:
            order = self.api.orders.get(order_id=order_id)
            item_list = [order]
        else:
            item_list = self.api.orders.list()

        classes = {'Order': Order,
                   'shipmentDetails': shipmentDetails,
                   'orderItems': OrderItem,
                   'billingDetails': billingDetails}

        if classname in ['shipmentDetails', 'orderItems', 'billingDetails']:
            item_list = self.extract_children(item_list, classname)

        class_object = [classes[classname](e) for e in item_list]

        return class_object

    def extract_children(self, order_list, classname):
        items = [[getattr(order, classname), order.orderId] for order in order_list]
        for item in items:
            order_id = item[1]
            if isinstance(item[0], list):
                for x in item[0]:
                    setattr(x, 'orderId', order_id)
            elif isinstance(item[0], dict):
                new_items = item[0]
                new_items['orderId'] = order_id
                return [new_items]

            else:
                setattr(item[0], 'orderId', item[1])

        flat_items = [item for sublist in items for item in sublist[0]]

        return flat_items
