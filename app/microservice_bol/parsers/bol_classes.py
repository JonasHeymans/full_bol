# from sqlalchemy import Column, Integer, String, TEXT, Float, Boolean, DateTime
#
# Base = 'nope'
# class Order(Base):
#     __tablename__ = 'orders'
#
#     def __init__(self):
#         pass
#
#     def __repr__(self):
#         return f"Order object"
#
#     order_id = Column(String(32), primary_key=True)
#     order_date = Column(DateTime)
#
#
# class OrderItem(Base):
#     __tablename__ = 'orderitems'
#
#     def __init__(self):
#         pass
#
#     order_item_id = Column(String(32), primary_key=True)
#
#     ean = Column(String(14))
#     title = Column(String(255))
#     quantity = Column(Integer)
#     offer_price = Column(Float)
#     offer_condition = Column(String(32))
#     offer_reference = Column(String(32))
#
#
# class Shipment(Base):
#     __tablename__ = 'shipments'
#
#     def __init__(self):
#         pass
#
#     def __repr__(self):
#         return f"Shipment object"
#
#     def add_tracking_code(self):
#         pass
#
#     shipment_id = Column(Integer, primary_key=True)
#     pickup_point = Column(Boolean)
#     shipment_date = Column(DateTime)
#     shipment_reference = Column(String(32))
#     customer_details = Column(TEXT)
#
#     billing_details = Column(TEXT)
#     detail_fetched = Column(Boolean, default=False)
#
#
# # class Seller(TimeStampedModel):
# #     first_name = models.CharField(_("Seller First Name"), max_length=255, blank=False, null=False)
# #     last_name = models.CharField(_("Seller Last Name"), max_length=255, blank=False, null=False)
# #     shop_name = models.CharField(_("Shop Name"), max_length=255, blank=False, null=False)
# #     client_id = models.CharField(_("Client ID"), max_length=100, blank=False, null=False)
# #     client_secret = models.CharField(_("Client Secret"), max_length=255, blank=False, null=False)
# #     last_synced_at = models.DateTimeField(_("Last synced at"), blank=True, null=True)
# #
# #     def __str__(self):
# #         return '{} {}'.format(self.first_name, self.last_name)
#
#
#
#
# class ShipmentItem(Base):
#     __tablename__ = 'shipmentitems'
#
#     def __init__(self):
#         pass
#
#     # shipment = models.ForeignKey(Shipment, _("Shipment"), blank=False, null=False)
#     # order = models.ForeignKey(Order, _("Order"), blank=False, null=False)
#     # order_item = models.ForeignKey(OrderItem, _("Order Item"), blank=False, null=False)
#
#     shipmentitem_id = Column(Integer, primary_key=True, autoincrement=True)
#
#     latest_delivery_date = Column(DateTime)
#     fulfilment_method = Column(String(3))
#
#     def __str__(self):
#         return '{} - {}'.format(self.shipment.id, self.order_item.title)
#
#
# # class Transport(TimeStampedModel):
# #     shipment = models.ForeignKey(Shipment, _("Shipment"), blank=False, null=False)
# #     transport_id = models.CharField(_("Transport ID"), primary_key=True, max_length=32, blank=False, null=False)
# #     transporter_code = models.CharField(_("Transporter Code"), max_length=32, blank=False, null=False)
# #     track_and_trace = models.CharField(_("Track and Trace"), max_length=32, blank=False, null=False)
# #
# #     # Shipping label could be a ForeignKey but for simplicity it is assumed part of the Transport
# #     shipping_label_id = models.CharField(_("Shipping Label ID"), max_length=32, blank=True, null=True)
# #     shipping_label_code = models.CharField(_("Shipping Label Code"), max_length=32, blank=True, null=True)
# #
# #     def __str__(self):
# #         return '{}'.format(self.transport_id)
