"""
Registry Parameters Enums

This module contains enums for registry-related API parameters based on the GBIF OpenAPI specification.
"""

from enum import Enum


class DatasetTypeEnum(Enum):
    """Dataset type enumeration"""
    OCCURRENCE = "OCCURRENCE"
    CHECKLIST = "CHECKLIST"
    METADATA = "METADATA"
    SAMPLING_EVENT = "SAMPLING_EVENT"


class DatasetSubtypeEnum(Enum):
    """Dataset subtype enumeration"""
    TAXONOMIC_AUTHORITY = "TAXONOMIC_AUTHORITY"
    NOMENCLATOR_AUTHORITY = "NOMENCLATOR_AUTHORITY"
    INVENTORY_THEMATIC = "INVENTORY_THEMATIC"
    INVENTORY_REGIONAL = "INVENTORY_REGIONAL"
    GLOBAL_SPECIES_DATASET = "GLOBAL_SPECIES_DATASET"
    DERIVED_FROM_OCCURRENCE = "DERIVED_FROM_OCCURRENCE"
    SPECIMEN = "SPECIMEN"
    OBSERVATION = "OBSERVATION"


class EndpointTypeEnum(Enum):
    """Endpoint type enumeration"""
    EML = "EML"
    FEED = "FEED"
    WFS = "WFS"
    WMS = "WMS"
    TCS_RDF = "TCS_RDF"
    TCS_XML = "TCS_XML"
    DWC_ARCHIVE = "DWC_ARCHIVE"
    DIGIR = "DIGIR"
    DIGIR_MANIS = "DIGIR_MANIS"
    TAPIR = "TAPIR"
    BIOCASE = "BIOCASE"
    BIOCASE_XML_ARCHIVE = "BIOCASE_XML_ARCHIVE"
    OAI_PMH = "OAI_PMH"
    COLDP = "COLDP"
    CAMTRAP_DP = "CAMTRAP_DP"
    BIOM_1_0 = "BIOM_1_0"
    BIOM_2_1 = "BIOM_2_1"
    ACEF = "ACEF"
    TEXT_TREE = "TEXT_TREE"
    OTHER = "OTHER"


class ContinentEnum(Enum):
    """Continent enumeration based on 7 continent model"""
    AFRICA = "AFRICA"
    ANTARCTICA = "ANTARCTICA"
    ASIA = "ASIA"
    OCEANIA = "OCEANIA"
    EUROPE = "EUROPE"
    NORTH_AMERICA = "NORTH_AMERICA"
    SOUTH_AMERICA = "SOUTH_AMERICA"


class LicenseEnum(Enum):
    """License enumeration"""
    CC0_1_0 = "CC0_1_0"
    CC_BY_4_0 = "CC_BY_4_0"
    CC_BY_NC_4_0 = "CC_BY_NC_4_0"
    UNSPECIFIED = "UNSPECIFIED"
    UNSUPPORTED = "UNSUPPORTED"
