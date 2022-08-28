import logging
import os

import requests

from mainapp.microservice_bol.constants.constants import DeliveryCode, ConditionName
from mainapp.microservice_bol.retailer.models.models import (
    Invoice,
    Invoices,
    InvoiceSpecification,
    Order,
    Orders,
    Offer,
    ProcessStatus,
    ProcessStatuses,
    Shipment,
    Shipments
)

__all__ = ["RetailerAPI"]

logger = logging.getLogger(__name__)


class MethodGroup(object):
    def __init__(self, api, group):
        self.api = api
        self.group = group

    def request(self, method, path="", params={}, **kwargs):
        uri = path
        if not uri.startswith("/"):
            base = "retailer-demo" if self.api.demo else "retailer"
            uri = f'/{base}/{self.group}{(f"/{path}" if path else "")}'
        return self.api.request(method, uri, params=params, **kwargs)


class OrderMethods(MethodGroup):
    def __init__(self, api):
        super(OrderMethods, self).__init__(api, "orders")

    def list(self, fulfilment_method=None, page=None):
        params = {}
        if fulfilment_method:
            params["fulfilment-method"] = fulfilment_method
        if page is not None:
            params["page"] = page
        resp = self.request("GET", params=params)
        logger.info(f'Got Orders: {params}')

        return Orders.parse(self.api, resp.text)

    def get(self, order_id):
        resp = self.request("GET", path=order_id)
        logger.info(f'Got Order with id: {order_id}')

        return Order.parse(self.api, resp.text)

    def ship_order_item(
            self,
            order_item_id,
            shipment_reference=None,
            shipping_label_code=None,
            transporter_code=None,
            track_and_trace=None,
    ):
        payload = {}
        payload['orderItems'] = [{'orderItemId': str(order_item_id)}]
        if shipment_reference:
            payload["shipmentReference"] = shipment_reference
        if shipping_label_code:
            payload["shippingLabelCode"] = shipping_label_code
        if transporter_code:
            payload.setdefault("transport", {})[
                "transporterCode"
            ] = transporter_code
        if track_and_trace:
            payload.setdefault("transport", {})[
                "trackAndTrace"
            ] = track_and_trace
        resp = self.request(
            "PUT", path="shipment", json=payload)

        logger.info(f'Shipped Order: {order_item_id}, payload = {payload}')

        return ProcessStatus.parse(self.api, resp.text)

    def cancel_order_item(self, order_item_id, reason_code):
        payload = {'orderItems': [
            {'orderItemId': order_item_id, "reasonCode": reason_code}
        ]}

        resp = self.request(
            "PUT", path=f"cancellation", json=payload
        )
        logger.info(f'Cancelled Order Item: {order_item_id}, payload = {payload}')

        return ProcessStatus.parse(self.api, resp.text)


class ShipmentMethods(MethodGroup):
    def __init__(self, api):
        super(ShipmentMethods, self).__init__(api, "shipments")

    def list(self, fulfilment_method=None, page=None, order_id=None):
        params = {}
        if fulfilment_method:
            params["fulfilment-method"] = fulfilment_method.value
        if page is not None:
            params["page"] = page
        if order_id:
            params["order_id"] = order_id
        resp = self.request("GET", params=params)
        logger.info(f'Got Shipments: {params}')

        return Shipments.parse(self.api, resp.text)

    def get(self, shipment_id):
        resp = self.request("GET", path=str(shipment_id))
        logger.info(f'Got Shipment with id: {shipment_id}')

        return Shipment.parse(self.api, resp.text)


class OfferMethods(MethodGroup):

    def __init__(self, api):
        super(OfferMethods, self).__init__(api, "offers")

    def create_offer(self,
                     ean,
                     bundle_prices,
                     stock_amount,
                     stock_managed_by_retailer=False,
                     condition_name=ConditionName.NEW,
                     condition_category=None,
                     condition_comment=None,
                     reference_code=None,
                     on_hold_by_retailer=None,
                     unknown_product_title=None,
                     fulfilment_type='FBR',
                     fulfilment_delivery_code=DeliveryCode.d_3_to_5d,
                     fulfilment_pick_up_points=None,

                     ):

        for x in bundle_prices:
            if list(x.keys()) != ['quantity', 'unitPrice']:
                print(x.keys())
                raise ValueError('Keys need to be quantity and unitPrice')

        payload = {'ean': ean,
                   'condition': {'name': condition_name},
                   'pricing': {'bundlePrices': bundle_prices},
                   'stock': {'amount': stock_amount,
                             'managedByRetailer': stock_managed_by_retailer},
                   'fulfilment': {'method': fulfilment_type}
                   }

        if condition_category:
            payload.setdefault("condition", {})[
                "category"
            ] = condition_category
        if condition_comment:
            payload.setdefault("condition", {})[
                "comment"
            ] = condition_comment
        if reference_code:
            payload["reference"] = reference_code
        if on_hold_by_retailer:
            payload["onHoldByRetailer"] = on_hold_by_retailer
        if unknown_product_title:
            payload["unknownProductTitle"] = unknown_product_title
        if fulfilment_type == 'FBR' or fulfilment_delivery_code:
            payload.setdefault("fulfilment", {})[
                "deliveryCode"
            ] = fulfilment_delivery_code
        if fulfilment_pick_up_points:
            payload.setdefault("fulfilment", {})[
                "pickUpPoints"
            ] = fulfilment_pick_up_points

        resp = self.request("POST", path="")

        logger.info(f'Created New Offer with EAN {ean}, payload = {payload}')

        return ProcessStatus.parse(self.api, resp.text)

    def get(self, offer_id):
        resp = self.request("GET", path=offer_id)
        logger.info(f'Got Offer with id {offer_id}')

        return Offer.parse(self.api, resp.text)

    def list(self):
        payload = {
            "format": "CSV"
        }
        resp = self.request("POST", path='export', json=payload)
        logger.info(f'Getting Offers')

        ProcessStatus.parse(self.api, resp.text)

    def update_offer(
            self,
            offer_id,
            reference_code=None,
            on_hold_by_retailer=None,
            unknown_product_title=None,
            fulfilment_type='FBR',
            fulfilment_delivery_code=DeliveryCode.d_3_to_5d,
            fulfilment_pick_up_points=None,
    ):

        payload = {'fulfilment': {'method': fulfilment_type}}

        if reference_code:
            payload["reference"] = reference_code
        if on_hold_by_retailer:
            payload["onHoldByRetailer"] = on_hold_by_retailer
        if unknown_product_title:
            payload["unknownProductTitle"] = unknown_product_title
        if fulfilment_type == 'FBR' or fulfilment_delivery_code:
            payload.setdefault("fulfilment", {})[
                "deliveryCode"
            ] = fulfilment_delivery_code
        if fulfilment_pick_up_points:
            payload.setdefault("fulfilment", {})[
                "pickUpPoints"
            ] = fulfilment_pick_up_points

        resp = self.request(
            "PUT", path=f"{offer_id}", json=payload)

        logger.info(f'Updated Offer with id {offer_id}, payload = {payload}')

        return ProcessStatus.parse(self.api, resp.text)

    def delete_offer(self, offer_id):
        self.request("DELETE", path=offer_id)
        logger.info(f'Deleted Offer with id: {offer_id}')

    def update_price(self,
                     offer_id,
                     bundle_prices: list
                     ):

        payload = {'pricing': {'bundlePrices': bundle_prices}}

        for x in bundle_prices:
            if list(x.keys()) != ['quantity', 'unitPrice']:
                print(x.keys())
                raise ValueError('Keys need to be quantity and unitPrice')

        resp = self.request("PUT", path=f"{offer_id}/price", json=payload)
        logger.info(f'Updated Prices for Offer with id {offer_id}, payload = {payload}')

        return ProcessStatus.parse(self.api, resp.text)

    def update_stock(self,
                     offer_id,
                     stock_amount,
                     managed_by_retailer=False
                     ):
        payload = {'amount': stock_amount, 'managedByRetailer': managed_by_retailer}
        resp = self.request("PUT", path=f"{offer_id}/stock", json=payload)
        logger.info(f'Updated Stock for Offer with id {offer_id}, payload = {payload} ')

        return ProcessStatus.parse(self.api, resp.text)


class ProcessStatusMethods(MethodGroup):
    def __init__(self, api):
        super(ProcessStatusMethods, self).__init__(api, "process-status")

    def get(self, entity_id, event_type, page=None):
        params = {"entity-id": entity_id, "event-type": event_type}
        if page:
            params["page"] = page
        resp = self.request("GET", params=params)

        logger.info(f'Got ProcessStatus: {params}')
        return ProcessStatuses.parse(self.api, resp.text)


class InvoiceMethods(MethodGroup):
    def __init__(self, api):
        super(InvoiceMethods, self).__init__(api, "invoices")

    def list(self, period_start=None, period_end=None):
        params = {}
        resp = self.request("GET", params=params)
        logger.info(f'Got Invoices: {params}')

        return Invoices.parse(self.api, resp.text)

    def get(self, invoice_id):
        resp = self.request("GET", path=str(invoice_id))
        logger.info(f'Got Invoice with id: {invoice_id}')

        return Invoice.parse(self.api, resp.text)

    def get_specification(self, invoice_id, page=None):
        params = {}
        if page is not None:
            params["page"] = page
        resp = self.request(
            "GET", path=f"{invoice_id}/specification", params=params
        )
        logger.info(f'Got Invoice Specification for Invoice with id:{invoice_id},  {params}')

        return InvoiceSpecification.parse(self.api, resp.text)


class RetailerAPI(object):
    def __init__(
            self,
            # test=False,
            timeout=None,
            session=None,
            demo=True,
            api_url=None,
            login_url=None,
            refresh_token=None,
    ):
        self.demo = demo
        self.api_url = api_url or "https://api.bol.com"
        self.login_url = login_url or "https://login.bol.com"
        self.timeout = timeout
        self.refresh_token = refresh_token
        self.orders = OrderMethods(self)
        self.offers = OfferMethods(self)
        self.shipments = ShipmentMethods(self)
        self.invoices = InvoiceMethods(self)
        self.process_status = ProcessStatusMethods(self)
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def login(self):
        data = {
            "client_secret": os.getenv('BOL_CLIENT_SECRET'),
            "grant_type": "client_credentials",
        }
        resp = self.session.post(
            self.login_url + "/token",
            auth=(os.getenv('BOL_CLIENT_ID'), os.getenv('BOL_CLIENT_SECRET')),
            data=data,
        )
        resp.raise_for_status()
        token = resp.json()
        self.set_access_token(token["access_token"])
        return token

    def refresh_access_token(
            self,
            username,
            password,
            refresh_token=None
    ):

        if refresh_token is None and self.refresh_token is None:
            raise ValueError("No 'refresh_token' provided")

        if refresh_token is None and self.refresh_token is not None:
            refresh_token = self.refresh_token

        params = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        resp = self.session.post(
            self.login_url + "/token",
            params=params,
            auth=(username, password),
        )
        resp.raise_for_status()
        data = resp.json()
        self.refresh_token = data["refresh_token"]
        self.set_access_token(data["access_token"])
        return data

    def set_access_token(self, access_token):
        self.session.headers.update(
            {
                "Authorization": "Bearer " + access_token,
                "Accept": "application/vnd.retailer.v6+json",
            }
        )

    def request(self, method, uri, params={}, **kwargs):
        request_kwargs = dict(**kwargs)
        request_kwargs.update(
            {
                "method": method,
                "url": self.api_url + uri,
                "params": params,
                "timeout": self.timeout,
            }
        )
        if "json" in request_kwargs:
            if "headers" not in request_kwargs:
                request_kwargs["headers"] = {}
            # If these headers are not added, the api returns a 400
            # Reference:
            #   https://api.bol.com/retailer/public/conventions/index.html
            request_kwargs["headers"].update({
                "content-type": "application/vnd.retailer.v6+json"
            })

        resp = self.session.request(**request_kwargs)
        resp.raise_for_status()
        return resp
