import enum

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

# class Language(enum.Enum):
#     nl = 'nl'
#     nlbe = 'nl-BE'
#     fr = 'fr'
#     frbe = 'fr-BE'

