import time
from support.database.database import DatabaseSession
from mainapp.microservice_bol.retailer.api.api import RetailerAPI
from mainapp.microservice_both.parsers.edc_order import EdcShipment
from support.logger.logger import Logger

log = Logger().get_commandline_logger('info')

with DatabaseSession() as session:

    api = RetailerAPI(demo=True)
    api.login()

    order_id = '1042823870'
    order_item_id = '6107434013'
    api.orders.list()
    api.orders.get(order_id)
    api.orders.cancel_order_item(order_id, 'OUT_OF_STOCK')

    shipment_id = '914587795'
    api.shipments.list()
    api.shipments.get(shipment_id)

    invoice_id = '4500022543921'
    api.invoices.list()
    api.invoices.get(invoice_id)
    api.invoices.get_specification(invoice_id)

    ean = '9780471117094'
    bundle_prices = [{
        "quantity": 1,
        "unitPrice": 9.99
    }, {
        "quantity": 6,
        "unitPrice": 8.99
    }, {
        "quantity": 12,
        "unitPrice": 7.99
    }]
    stock_amount = 1
    offer_id = '13722de8-8182-d161-5422-4a0a1caab5c8'
    reference_code = 'Testing'
    on_hold_by_retailer = True
    unknown_product_title = True
    fulfilment_type = 'FBB'
    api.offers.create_offer(ean, bundle_prices, stock_amount)
    api.offers.get(offer_id)
    time.sleep(1)
    api.offers.update_offer(offer_id)
    api.offers.delete_offer(offer_id)
    api.offers.update_price(offer_id, bundle_prices)
    api.offers.update_stock(offer_id, stock_amount)

