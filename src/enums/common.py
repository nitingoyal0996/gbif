from enum import Enum

class ContinentEnum(str, Enum):
    """
    The continent, based on a 7 continent model.
    See the GBIF Continents project for the exact divisions.
    This is a geographical division. See `GBIFRegion` for GBIF's political divisions.
    """

    AFRICA = "AFRICA"
    ANTARCTICA = "ANTARCTICA"
    ASIA = "ASIA"
    OCEANIA = "OCEANIA"
    EUROPE = "EUROPE"
    NORTH_AMERICA = "NORTH_AMERICA"
    SOUTH_AMERICA = "SOUTH_AMERICA"

    def __str__(self):
        return self.value


class GbifRegionEnum(str, Enum):
    AFRICA = "AFRICA"
    ASIA = "ASIA"
    EUROPE = "EUROPE"
    NORTH_AMERICA = "NORTH_AMERICA"
    OCEANIA = "OCEANIA"
    LATIN_AMERICA = "LATIN_AMERICA"
    ANTARCTICA = "ANTARCTICA"

    def __str__(self):
        return self.value


class LicenseEnum(str, Enum):
    """A legal document giving official permission to do something with the occurrence."""

    CC0_1_0 = "CC0_1_0"
    CC_BY_4_0 = "CC_BY_4_0"
    CC_BY_NC_4_0 = "CC_BY_NC_4_0"
    UNSPECIFIED = "UNSPECIFIED"
    UNSUPPORTED = "UNSUPPORTED"

    def __str__(self):
        return self.value


class MediaObjectTypeEnum(str, Enum):
    """The kind of media object."""

    StillImage = "StillImage"
    MovingImage = "MovingImage"
    Sound = "Sound"
    InteractiveResource = "InteractiveResource"

    def __str__(self):
        return self.value
