# Bol documentation

original source: https://github.com/pennersr/python-bol-api

bol.com reference: https://api.bol.com/retailer/public/redoc/v6#

Migration Guide: https://api.bol.com/retailer/public/Retailer-API/v6/migrationguide/v4-v6/migrationguide.html

Test cases: https://api.bol.com/retailer/public/Retailer-API/demo/v6-COMMISSIONS.html

## Orders

All bol.com API- requests are implemented.

Form of this documentation: <bol_API_name> : <method_in_program>
  
- Get open orders: api.orders.list()

- Get an open order by order id: api.orders.get(order_id)

- Cancel an order item by order item id:
api.orders.cancel_order_item(order_item_id, reason_code)

- Ship order item: api.orders.ship_order_item(order_item_id, 
shipment_reference, shipping_label_code,transporter_code,track_and_trace,))


## Shipments

All bol.com API- requests are implemented.

- Get shipment list: api.shipments.list()

- Get a shipment by shipment id: api.shipments.get(shipment_id)

## Invoices

All bol.com API- requests are implemented.

- Get all invoices: api.invoices.list()

- Get an invoice by invoice id: api.invoices.get(invoice_id)
- Get an invoice specification by invoice id:  api.invoices.get_specification(invoice_id, page)
    - page (optional) = "The page to get. Each page contains a maximum of 110.000 lines."


## ProcessStatus

- ? Don't know how this works

- Example ProcessStatus: 
    - id: 1234567
    - entityId: 987654321
    - eventType: PROCESS_EXAMPLE
    - description: Example request for processing 987654321.
    - status: SUCCESS
    - errorMessage: The example has been processed.
    - createTimestamp: 2018-11-14T09:34:41+01:00
    - links:
        - rel: self
        - href: https://api.bol.com/retailer/process-status/1234567
        - method: GET


## Offers
- Create a new offer: api.offers.create_offer
(ean,bundle_prices,stock_amount)
    - This is the most minimal implementation. Many more parameters are available.
    
- Request an offer export file: **Not implemented yet**
- Retrieve an offer export file by offer export id: **Not implemented yet**
- Retrieve an offer by its offer id: api.offers.get(offer_id')
    - Eg. offer.pricing.bundlePrices[0].price to get one of the prices. Note the '[0]', 
    because each offer can have multiple prices due to Volumekorting
 - Update an offer: api.offers.update_offer(offer_id)
    - defaults to 'FBR' and delivery_time '3-5d'
- Delete offer by id :  api.offers.delete_offer(offer_id)
- Update price(s) for offer by id: api.offers.update_price(offer_id,bundle_prices: list)
    - 'bundle_prices' is a list of dicts containing 
    the prices per amount bought. Eg. "if you buy one item, 
    the price is 14.99, if you buy 2 the price for each is 12.99,.."
- Update stock for offer by id: api.offers.update_stock(offer_id,amount)
    - Please note that 'managed_by_retailer' is set to False


