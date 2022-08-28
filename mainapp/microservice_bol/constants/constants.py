import enum


class FulfilmentMethod(enum.Enum):
    """
    The fulfilment method. Fulfilled by the retailer (FBR) or fulfilled by
    microservice_supplier.com (FBB).
    """

    FBR = "FBR"
    FBB = "FBB"


class TransporterCode(enum.Enum):
    """
    https://api.bol.com/retailer/public/redoc/v3#tag/Transports
    """

    BPOST_BE = "BPOST_BE"
    BPOST_BRIEF = "BPOST_BRIEF"
    BRIEFPOST = "BRIEFPOST"
    COURIER = "COURIER"
    DHL = "DHL"
    DHLFORYOU = "DHLFORYOU"
    DHL_DE = "DHL_DE"
    DHL_GLOBAL_MAIL = "DHL-GLOBAL-MAIL"
    DPD_BE = "DPD-BE"
    DPD_NL = "DPD-NL"
    DYL = "DYL"
    FEDEX_BE = "FEDEX_BE"
    FEDEX_NL = "FEDEX_NL"
    FIEGE = "FIEGE"
    GLS = "GLS"
    LOGOIX = "LOGOIX"
    OTHER = "OTHER"
    PACKS = "PACKS"
    PARCEL_NL = "PARCEL-NL"
    RJP = "RJP"
    TNT = "TNT"
    TNT_BRIEF = "TNT_BRIEF"
    TNT_EXPRESS = "TNT-EXPRESS"
    TNT_EXTRA = "TNT-EXTRA"
    TRANSMISSION = "TRANSMISSION"
    TSN = "TSN"
    UPS = "UPS"


class CancellationReasonCode(enum.Enum):
    OUT_OF_STOCK = "OUT_OF_STOCK"
    REQUESTED_BY_CUSTOMER = "REQUESTED_BY_CUSTOMER"
    BAD_CONDITION = "BAD_CONDITION"
    HIGHER_SHIPCOST = "HIGHER_SHIPCOST"
    INCORRECT_PRICE = "INCORRECT_PRICE"
    NOT_AVAIL_IN_TIME = "NOT_AVAIL_IN_TIME"
    NO_BOL_GUARANTEE = "NO_BOL_GUARANTEE"
    ORDERED_TWICE = "ORDERED_TWICE"
    RETAIN_ITEM = "RETAIN_ITEM"
    TECH_ISSUE = "TECH_ISSUE"
    UNFINDABLE_ITEM = "UNFINDABLE_ITEM"
    OTHER = "OTHER"


class DeliveryCode(enum.Enum):
    d_24uurs_23 = "24uurs-23"
    d_24uurs_22 = "24uurs-22"
    d_24uurs_21 = "24uurs-21"
    d_24uurs_20 = "24uurs-20"
    d_24uurs_19 = "24uurs-19"
    d_24uurs_18 = "24uurs-18"
    d_24uurs_17 = "24uurs-17"
    d_24uurs_16 = "24uurs-16"
    d_24uurs_15 = "24uurs-15"
    d_24uurs_14 = "24uurs-14"
    d_24uurs_13 = "24uurs-13"
    d_24uurs_11 = "24uurs-12"
    d_1_to_2d = "1-2d"
    d_2_to_3d = "2-3d"
    d_3_to_5d = "3-5d"
    d_4_to_8d = "4-8d"
    d_1_to_8d = "1-8d"
    d_mijn_leverbelofte = '"MijnLeverbelofte"'


class ConditionName(enum.Enum):
    NEW = "NEW"
    AS_NEW = "AS_NEW"
    GOOD = "GOOD"
    REASONABLE = "REASONABLE"
    MODERATE = "MODERATE"


class TimeFrameType(enum.Enum):
    REGULAR = 'REGULAR'
    EVENING = 'EVENING'
    APPOINTMENT = 'APPOINTMENT'
    SAMEDAY = 'SAMEDAY'
    SUNDAY = 'SUNDAY'


class DistributionParty(enum.Enum):
    RETAILER = 'RETAILER'
    BOL = 'BOL'


class Salutation(enum.Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    UNKNOWN = 'UNKNOWN'
