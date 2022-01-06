from mainapp.microservice_both.parsers.edc_order import EdcShipment

class OrderAdapter:

    def setup_shipment(self, file):
        return [EdcShipment(file)]