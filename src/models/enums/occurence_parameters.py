from enum import Enum

class BasisOfRecordEnum(str, Enum):
    """
    The values of the Darwin Core term Basis of Record which can apply to occurrences.
    See GBIF's Darwin Core Type Vocabulary for definitions.
    """

    PRESERVED_SPECIMEN = "PRESERVED_SPECIMEN"
    FOSSIL_SPECIMEN = "FOSSIL_SPECIMEN"
    LIVING_SPECIMEN = "LIVING_SPECIMEN"
    OBSERVATION = "OBSERVATION"
    HUMAN_OBSERVATION = "HUMAN_OBSERVATION"
    MACHINE_OBSERVATION = "MACHINE_OBSERVATION"
    MATERIAL_SAMPLE = "MATERIAL_SAMPLE"
    LITERATURE = "LITERATURE"
    MATERIAL_CITATION = "MATERIAL_CITATION"
    OCCURRENCE = "OCCURRENCE"
    UNKNOWN = "UNKNOWN"

    def __str__(self):
        return self.value


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


class OccurrenceStatusEnum(str, Enum):
    """
    A statement about the presence or absence of a Taxon at a Location.
    For definitions, see the GBIF occurrence status vocabulary.
    """

    PRESENT = "PRESENT"
    ABSENT = "ABSENT"

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
