# models.py
# Generated from OpenAPI specification for the GBIF Occurrence API.
# These models include detailed descriptions, examples, and follow Pydantic
# best practices for production use, including immutability, strict data
# contracts, and value constraints to guide LLM applications.

from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict, Union, Any
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)
from datetime import datetime
from uuid import UUID

# --- Pydantic Model Configuration ---


class ProductionBaseModel(BaseModel):
    """A base model with production-ready settings."""

    model_config = ConfigDict(
        frozen=True,  # Models are immutable
        extra="forbid",  # Forbid extra fields not in the model
        populate_by_name=True,  # Allow population by field name OR alias
    )


# --- Enum Definitions with Descriptions ---


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


class OccurrenceStatusEnum(str, Enum):
    """
    A statement about the presence or absence of a Taxon at a Location.
    For definitions, see the GBIF occurrence status vocabulary.
    """

    PRESENT = "PRESENT"
    ABSENT = "ABSENT"


class LicenseEnum(str, Enum):
    """A legal document giving official permission to do something with the occurrence."""

    CC0_1_0 = "CC0_1_0"
    CC_BY_4_0 = "CC_BY_4_0"
    CC_BY_NC_4_0 = "CC_BY_NC_4_0"
    UNSPECIFIED = "UNSPECIFIED"
    UNSUPPORTED = "UNSUPPORTED"


class ProtocolEnum(str, Enum):
    """The technical protocol by which this occurrence was retrieved from the publisher's systems."""

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


class AgentIdentifierTypeEnum(str, Enum):
    """Type of agent identifier."""

    ORCID = "ORCID"
    WIKIDATA = "WIKIDATA"
    OTHER = "OTHER"


class IdentifierTypeEnum(str, Enum):
    """Type of identifier."""

    URL = "URL"
    LSID = "LSID"
    HANDLER = "HANDLER"
    DOI = "DOI"
    UUID = "UUID"
    FTP = "FTP"
    URI = "URI"
    UNKNOWN = "UNKNOWN"
    GBIF_PORTAL = "GBIF_PORTAL"
    GBIF_NODE = "GBIF_NODE"
    GBIF_PARTICIPANT = "GBIF_PARTICIPANT"
    GRSCICOLL_ID = "GRSCICOLL_ID"
    GRSCICOLL_URI = "GRSCICOLL_URI"
    IH_IRN = "IH_IRN"
    ROR = "ROR"
    GRID = "GRID"
    CITES = "CITES"
    SYMBIOTA_UUID = "SYMBIOTA_UUID"
    WIKIDATA = "WIKIDATA"
    NCBI_BIOCOLLECTION = "NCBI_BIOCOLLECTION"
    ISIL = "ISIL"
    CLB_DATASET_KEY = "CLB_DATASET_KEY"


class MediaObjectTypeEnum(str, Enum):
    """The kind of media object."""

    StillImage = "StillImage"
    MovingImage = "MovingImage"
    Sound = "Sound"
    InteractiveResource = "InteractiveResource"


class TaxonRankEnum(str, Enum):
    """The taxonomic rank of the most specific name in the scientificName."""

    DOMAIN = "DOMAIN"
    SUPERKINGDOM = "SUPERKINGDOM"
    KINGDOM = "KINGDOM"
    SUBKINGDOM = "SUBKINGDOM"
    INFRAKINGDOM = "INFRAKINGDOM"
    SUPERPHYLUM = "SUPERPHYLUM"
    PHYLUM = "PHYLUM"
    SUBPHYLUM = "SUBPHYLUM"
    INFRAPHYLUM = "INFRAPHYLUM"
    SUPERCLASS = "SUPERCLASS"
    CLASS = "CLASS"
    SUBCLASS = "SUBCLASS"
    INFRACLASS = "INFRACLASS"
    PARVCLASS = "PARVCLASS"
    SUPERLEGION = "SUPERLEGION"
    LEGION = "LEGION"
    SUBLEGION = "SUBLEGION"
    INFRALEGION = "INFRALEGION"
    SUPERCOHORT = "SUPERCOHORT"
    COHORT = "COHORT"
    SUBCOHORT = "SUBCOHORT"
    INFRACOHORT = "INFRACOHORT"
    MAGNORDER = "MAGNORDER"
    SUPERORDER = "SUPERORDER"
    GRANDORDER = "GRANDORDER"
    ORDER = "ORDER"
    SUBORDER = "SUBORDER"
    INFRAORDER = "INFRAORDER"
    PARVORDER = "PARVORDER"
    SUPERFAMILY = "SUPERFAMILY"
    FAMILY = "FAMILY"
    SUBFAMILY = "SUBFAMILY"
    INFRAFAMILY = "INFRAFAMILY"
    SUPERTRIBE = "SUPERTRIBE"
    TRIBE = "TRIBE"
    SUBTRIBE = "SUBTRIBE"
    INFRATRIBE = "INFRATRIBE"
    SUPRAGENERIC_NAME = "SUPRAGENERIC_NAME"
    GENUS = "GENUS"
    SUBGENUS = "SUBGENUS"
    INFRAGENUS = "INFRAGENUS"
    SECTION = "SECTION"
    SUBSECTION = "SUBSECTION"
    SERIES = "SERIES"
    SUBSERIES = "SUBSERIES"
    INFRAGENERIC_NAME = "INFRAGENERIC_NAME"
    SPECIES_AGGREGATE = "SPECIES_AGGREGATE"
    SPECIES = "SPECIES"
    INFRASPECIFIC_NAME = "INFRASPECIFIC_NAME"
    GREX = "GREX"
    SUBSPECIES = "SUBSPECIES"
    CULTIVAR_GROUP = "CULTIVAR_GROUP"
    CONVARIETY = "CONVARIETY"
    INFRASUBSPECIFIC_NAME = "INFRASUBSPECIFIC_NAME"
    PROLES = "PROLES"
    RACE = "RACE"
    NATIO = "NATIO"
    ABERRATION = "ABERRATION"
    MORPH = "MORPH"
    VARIETY = "VARIETY"
    SUBVARIETY = "SUBVARIETY"
    FORM = "FORM"
    SUBFORM = "SUBFORM"
    PATHOVAR = "PATHOVAR"
    BIOVAR = "BIOVAR"
    CHEMOVAR = "CHEMOVAR"
    MORPHOVAR = "MORPHOVAR"
    PHAGOVAR = "PHAGOVAR"
    SEROVAR = "SEROVAR"
    CHEMOFORM = "CHEMOFORM"
    FORMA_SPECIALIS = "FORMA_SPECIALIS"
    CULTIVAR = "CULTIVAR"
    STRAIN = "STRAIN"
    OTHER = "OTHER"
    UNRANKED = "UNRANKED"


class TaxonomicStatusEnum(str, Enum):
    """The status of the use of the scientificName as a label for a taxon."""

    ACCEPTED = "ACCEPTED"
    DOUBTFUL = "DOUBTFUL"
    SYNONYM = "SYNONYM"
    HETEROTYPIC_SYNONYM = "HETEROTYPIC_SYNONYM"
    HOMOTYPIC_SYNONYM = "HOMOTYPIC_SYNONYM"
    PROPARTE_SYNONYM = "PROPARTE_SYNONYM"
    MISAPPLIED = "MISAPPLIED"
    AMBIGUOUS_SYNONYM = "AMBIGUOUS_SYNONYM"
    PROVISIONALLY_ACCEPTED = "PROVISIONALLY_ACCEPTED"


class GBIFRegionEnum(str, Enum):
    """
    An enumeration for all GBIF Regions. These are based on IPBES regions.
    This is a political division, part of GBIF's governance structure.
    """

    AFRICA = "AFRICA"
    ASIA = "ASIA"
    EUROPE = "EUROPE"
    NORTH_AMERICA = "NORTH_AMERICA"
    OCEANIA = "OCEANIA"
    LATIN_AMERICA = "LATIN_AMERICA"
    ANTARCTICA = "ANTARCTICA"


# --- Predicate Model Definitions ---


class Predicate(ProductionBaseModel):
    """A predicate defining filters to apply for a search or download."""

    type: str = Field(..., description="The type of predicate.")


class ConjunctionPredicate(Predicate):
    """A logical conjunction ('AND') of a list of sub-predicates."""

    type: str = Field("and", description="The type of predicate, fixed to 'and'.")
    predicates: List[AnyPredicate] = Field(
        ..., description="The list of sub-predicates to combine with a logical AND."
    )


class DisjunctionPredicate(Predicate):
    """A logical disjunction ('OR') of a list of sub-predicates."""

    type: str = Field("or", description="The type of predicate, fixed to 'or'.")
    predicates: List[AnyPredicate] = Field(
        ..., description="The list of sub-predicates to combine with a logical OR."
    )


class EqualsPredicate(Predicate):
    """This predicate checks if its `key` is equal to its `value`."""

    type: str = Field("equals", description="The type of predicate, fixed to 'equals'.")
    key: str = Field(
        ..., description="The search parameter to test.", examples=["COUNTRY"]
    )
    value: str = Field(..., description="The value to test for.", examples=["FR"])
    matchCase: Optional[bool] = Field(
        False,
        description="Whether to match letter case (UPPER or lower case) on string value comparisons.",
    )
    checklistKey: Optional[str] = Field(
        None, description="Specify which taxonomy to use."
    )


class FullTextSearchPredicate(Predicate):
    """This predicate performs a full-text search based on a query parameter. Not currently supported for occurrence downloads."""

    type: str = Field(
        "fullTextSearch",
        description="The type of predicate, fixed to 'fullTextSearch'.",
    )
    key: str = Field(..., description="The search parameter to test.")
    q: str = Field(..., description="The full-text search query.")


class GeoDistancePredicate(Predicate):
    """This predicate checks if an occurrence falls within a distance of a location."""

    type: str = Field(
        "geoDistance", description="The type of predicate, fixed to 'geoDistance'."
    )
    latitude: str = Field(
        ..., description="The latitude of the location.", examples=["40.7128"]
    )
    longitude: str = Field(
        ..., description="The longitude of the location.", examples=["-74.0060"]
    )
    distance: str = Field(
        ...,
        description="The distance as a number and unit, e.g. `5km` or `5000m`.",
        examples=["10km"],
    )


class GreaterThanOrEqualsPredicate(Predicate):
    """This predicate checks if its `key` is greater than or equal to its `value`."""

    type: str = Field(
        "greaterThanOrEquals",
        description="The type of predicate, fixed to 'greaterThanOrEquals'.",
    )
    key: str = Field(
        ..., description="The search parameter to test.", examples=["YEAR"]
    )
    value: str = Field(..., description="The value to test for.", examples=["2017"])
    matchCase: Optional[bool] = Field(
        False, description="Whether to match letter case on string value comparisons."
    )


class GreaterThanPredicate(Predicate):
    """This predicate checks if its `key` is greater than its `value`."""

    type: str = Field(
        "greaterThan", description="The type of predicate, fixed to 'greaterThan'."
    )
    key: str = Field(
        ..., description="The search parameter to test.", examples=["ELEVATION"]
    )
    value: str = Field(..., description="The value to test for.", examples=["1000"])
    matchCase: Optional[bool] = Field(
        False, description="Whether to match letter case on string value comparisons."
    )


class SearchParameter(ProductionBaseModel):
    """
    The search parameter to test. This could be refined to an Enum or Literal
    if the set of valid search parameters is known and finite.
    """

    pass


class InPredicate(Predicate):
    """This predicate checks if its `key` is equal to any of its `values`."""

    type: str = Field("in", description="The type of predicate, fixed to 'in'.")
    key: SearchParameter = Field(..., description="The search parameter to test.")
    values: List[str] = Field(
        ...,
        description="The list of values to test for.",
        examples=[["PRESERVED_SPECIMEN", "OBSERVATION"]],
    )
    matchCase: Optional[bool] = Field(
        False, description="Whether to match letter case on string value comparisons."
    )
    checklistKey: Optional[str] = Field(
        None, description="Specify which taxonomy to use."
    )


class IsNotNullPredicate(Predicate):
    """This predicate checks if the `parameter` is not null (has a value)."""

    type: str = Field(
        "isNotNull", description="The type of predicate, fixed to 'isNotNull'."
    )
    parameter: SearchParameter = Field(
        ..., description="The search parameter to test for existence."
    )
    checklistKey: Optional[str] = Field(
        None, description="Specify which taxonomy to use."
    )


class IsNullPredicate(Predicate):
    """This predicate checks if its `parameter` is null (is empty)."""

    type: str = Field("isNull", description="The type of predicate, fixed to 'isNull'.")
    parameter: SearchParameter = Field(
        ..., description="The search parameter to test for absence."
    )
    checklistKey: Optional[str] = Field(
        None, description="Specify which taxonomy to use."
    )


class LessThanOrEqualsPredicate(Predicate):
    """This predicate checks if its `key` is less than or equal to its `value`."""

    type: str = Field(
        "lessThanOrEquals",
        description="The type of predicate, fixed to 'lessThanOrEquals'.",
    )
    key: str = Field(
        ..., description="The search parameter to test.", examples=["YEAR"]
    )
    value: str = Field(..., description="The value to test for.", examples=["2000"])
    matchCase: Optional[bool] = Field(
        False, description="Whether to match letter case on string value comparisons."
    )


class LessThanPredicate(Predicate):
    """This predicate checks if its `key` is less than its `value`."""

    type: str = Field(
        "lessThan", description="The type of predicate, fixed to 'lessThan'."
    )
    key: str = Field(
        ..., description="The search parameter to test.", examples=["ELEVATION"]
    )
    value: str = Field(..., description="The value to test for.", examples=["500"])
    matchCase: Optional[bool] = Field(
        False, description="Whether to match letter case on string value comparisons."
    )


class LikePredicate(Predicate):
    """This predicate checks if its `key` matches a simple pattern in the `value`. `?` matches a single character, and `*` matches zero or more characters."""

    type: str = Field("like", description="The type of predicate, fixed to 'like'.")
    key: str = Field(
        ..., description="The search parameter to test.", examples=["SCIENTIFIC_NAME"]
    )
    value: str = Field(
        ...,
        description="The pattern value to test for (e.g., 'A*').",
        examples=["Puma con*"],
    )
    checklistKey: Optional[str] = Field(
        None, description="Specify which taxonomy to use."
    )
    matchCase: Optional[bool] = Field(
        False, description="Whether to match letter case on string value comparisons."
    )


class NotPredicate(Predicate):
    """This predicate negates its subpredicate."""

    type: str = Field("not", description="The type of predicate, fixed to 'not'.")
    predicate: AnyPredicate = Field(..., description="The predicate to be negated.")


class RangeValue(ProductionBaseModel):
    """The range value to test for."""

    gte: Optional[str] = Field(None, description="Greater than or equal to.")
    gt: Optional[str] = Field(None, description="Greater than.")
    lte: Optional[str] = Field(None, description="Less than or equal to.")
    lt: Optional[str] = Field(None, description="Less than.")


class RangePredicate(Predicate):
    """This predicate checks if its `key` is within the range `value`."""

    type: str = Field("range", description="The type of predicate, fixed to 'range'.")
    key: SearchParameter = Field(..., description="The search parameter to test.")
    value: RangeValue = Field(..., description="The range of values to test for.")


class WithinPredicate(Predicate):
    """This predicate checks if an occurrence falls within the given WKT geometry."""

    type: str = Field("within", description="The type of predicate, fixed to 'within'.")
    geometry: str = Field(
        ...,
        description="The WKT geometry to test for. Occurrences whose location is within this geometry are returned.",
        examples=["POLYGON((30.1 10.1, 40 40, 20 40, 10 20, 30.1 10.1))"],
    )


# Discriminated union of all possible predicate types
AnyPredicate = Union[
    ConjunctionPredicate,
    DisjunctionPredicate,
    EqualsPredicate,
    FullTextSearchPredicate,
    GeoDistancePredicate,
    GreaterThanOrEqualsPredicate,
    GreaterThanPredicate,
    InPredicate,
    IsNotNullPredicate,
    IsNullPredicate,
    LessThanOrEqualsPredicate,
    LessThanPredicate,
    LikePredicate,
    NotPredicate,
    RangePredicate,
    WithinPredicate,
]


class OccurrencePredicateSearchRequest(ProductionBaseModel):
    """Request body for a predicate-based occurrence search."""

    predicate: Optional[AnyPredicate] = Field(
        None,
        description="The root predicate for the search.",
        examples=[
            {
                "type": "and",
                "predicates": [
                    {"type": "equals", "key": "COUNTRY", "value": "FR"},
                    {"type": "equals", "key": "YEAR", "value": "2017"},
                ],
            }
        ],
    )


# --- Main Model Definitions ---


class AgentIdentifier(ProductionBaseModel):
    """A globally unique identifier for a person, group, or organization."""

    type: Optional[AgentIdentifierTypeEnum] = Field(
        None, description="The type of identifier (e.g., ORCID)."
    )
    value: str = Field(
        ...,
        description="The value of the identifier.",
        examples=["https://orcid.org/0000-0001-6492-4016"],
    )


class Usage(ProductionBaseModel):
    """Represents a taxonomic name usage."""

    key: Optional[str] = Field(None, description="The key for the name usage.")
    name: Optional[str] = Field(None, description="The scientific name.")
    rank: Optional[str] = Field(None, description="The taxonomic rank.")
    code: Optional[str] = Field(None, description="The nomenclatural code.")
    authorship: Optional[str] = Field(None, description="The authorship of the name.")
    genericName: Optional[str] = Field(None)
    infragenericEpithet: Optional[str] = Field(None)
    specificEpithet: Optional[str] = Field(None)
    infraspecificEpithet: Optional[str] = Field(None)
    formattedName: Optional[str] = Field(
        None, description="The name formatted with authorship and italics."
    )


class RankedName(ProductionBaseModel):
    """A taxonomic name with its rank and key."""

    key: Optional[str] = Field(None, description="The key for the name.")
    name: Optional[str] = Field(None, description="The scientific name.")
    rank: Optional[str] = Field(None, description="The taxonomic rank.")
    authorship: Optional[str] = Field(None, description="The authorship of the name.")


class Classification(ProductionBaseModel):
    """The map of classifications associated with this occurrence keyed by checklistKey."""

    usage: Optional[Usage] = Field(None, description="The direct name usage matched.")
    acceptedUsage: Optional[Usage] = Field(
        None, description="The accepted name usage if the matched usage was a synonym."
    )
    taxonomicStatus: Optional[str] = Field(
        None, description="The taxonomic status of the matched name usage."
    )
    classification: Optional[List[RankedName]] = Field(
        None,
        description="The full classification path from kingdom to the matched usage.",
    )
    iucnRedListCategoryCode: Optional[str] = Field(
        None, description="The IUCN Red List category code."
    )
    issues: Optional[List[str]] = Field(
        None, description="Any issues encountered during taxonomic interpretation."
    )


class Count(ProductionBaseModel):
    """A facet count for a specific value."""

    name: Optional[str] = Field(None, description="The value for the facet.")
    count: Optional[int] = Field(
        None, description="The number of records with this value."
    )


class FacetOccurrenceSearchParameter(ProductionBaseModel):
    """The resulting facets of a search operation."""

    field: Optional[str] = Field(None, description="The faceted field.")
    counts: Optional[List[Count]] = Field(None, description="The list of facet counts.")


class GadmFeature(ProductionBaseModel):
    """A region from the GADM database."""

    gid: Optional[str] = Field(
        None,
        description="The identifier in GADM for the administrative division.",
        examples=["AGO.1_1"],
    )
    name: str = Field(
        ...,
        description="The English name in GADM for the administrative division.",
        examples=["Bengo"],
    )


class Gadm(ProductionBaseModel):
    """The administrative divisions according to the GADM database."""

    level0: Optional[GadmFeature] = Field(
        None, description="GADM level 0 feature (country)."
    )
    level1: Optional[GadmFeature] = Field(
        None, description="GADM level 1 feature (state/province)."
    )
    level2: Optional[GadmFeature] = Field(
        None, description="GADM level 2 feature (county/district)."
    )
    level3: Optional[GadmFeature] = Field(None, description="GADM level 3 feature.")


class Identifier(ProductionBaseModel):
    """Alternative identifiers for the occurrence."""

    identifier: str = Field(
        ...,
        description="The identifier string.",
        examples=["URN:catalog:UWBM:Bird:126493"],
    )
    title: Optional[str] = Field(
        None, description="The optional title of an identifier, mostly for linking."
    )
    type: IdentifierTypeEnum = Field(..., description="Type of identifier.")
    identifierLink: Optional[str] = Field(
        None,
        description="An HTTP link for an identifier, if a suitable, known resolver exists.",
    )


class IsoDateInterval(ProductionBaseModel):
    """
    The date-time during which an Event occurred. The structure of the 'from' and 'to'
    fields can vary, hence they are typed broadly.
    """

    from_: Optional[Dict[Any, Any]] = Field(
        None, alias="from", description="The lower bound of the date interval."
    )
    to: Optional[Dict[Any, Any]] = Field(
        None, description="The upper bound of the date interval."
    )


class MeasurementOrFact(ProductionBaseModel):
    """Measurements or facts about the occurrence."""

    id: str = Field(..., description="Identifier for the measurement or fact.")
    type: str = Field(
        ...,
        description="The nature of the measurement, fact, characteristic, or assertion.",
    )
    value: str = Field(
        ...,
        description="The value of the measurement, fact, characteristic, or assertion.",
    )
    unit: Optional[str] = Field(
        None, description="The units for the value of the measurement."
    )
    accuracy: Optional[str] = Field(
        None, description="The description of the uncertainty around the value."
    )
    method: Optional[str] = Field(
        None,
        description="A description of or reference to the method used to determine the measurement or fact.",
    )
    determinedBy: Optional[str] = Field(
        None,
        description="A list of names of people, groups, or organizations who determined the measurement or fact.",
    )
    determinedDate: Optional[str] = Field(
        None, description="The date on which the measurement or fact was determined."
    )
    remarks: Optional[str] = Field(
        None, description="Comments or notes about the measurement or fact."
    )


class MediaObject(ProductionBaseModel):
    """Multimedia related to the occurrence."""

    type: MediaObjectTypeEnum = Field(..., description="The kind of media object.")
    format: Optional[str] = Field(
        None, description="The format the image is exposed in (e.g., 'image/jpeg')."
    )
    references: Optional[str] = Field(
        None, description="An HTML webpage that shows the image or its metadata."
    )
    title: Optional[str] = Field(None, description="The media item title.")
    description: Optional[str] = Field(
        None, description="A longer description for this media item."
    )
    source: Optional[str] = Field(None, description="The source of the media item.")
    audience: Optional[str] = Field(
        None,
        description="A class or description for whom the image is intended or useful.",
    )
    created: Optional[datetime] = Field(
        None, description="The date and time this media item was created."
    )
    creator: Optional[str] = Field(
        None, description="The person that created the media item."
    )
    contributor: Optional[str] = Field(
        None, description="Any contributor in addition to the creator."
    )
    publisher: Optional[str] = Field(
        None, description="An entity responsible for making the media item available."
    )
    license: Optional[str] = Field(None, description="License for this media item.")
    rightsHolder: Optional[str] = Field(
        None,
        description="A person or organization owning or managing rights over the media item.",
    )
    identifier: str = Field(
        ..., description="The public URL that identifies and locates the media item."
    )


class OccurrenceRelation(ProductionBaseModel):
    """Relationships between occurrences."""

    id: Optional[str] = Field(None, description="Identifier for the relationship.")
    occurrenceId: Optional[int] = Field(
        None, description="The subject of the relationship."
    )
    relatedOccurrenceId: Optional[int] = Field(
        None, description="The object of the relationship."
    )
    type: Optional[str] = Field(
        None, description="The type of relationship (e.g., 'sameSpecimenAs')."
    )
    accordingTo: Optional[str] = Field(
        None, description="The source of the relationship assertion."
    )
    establishedDate: Optional[str] = Field(
        None, description="The date the relationship was established."
    )
    remarks: Optional[str] = Field(None, description="Notes on the relationship.")


class MediaType(ProductionBaseModel):
    """Represents a media type (e.g., 'application/json')."""

    type: Optional[str] = Field(None)
    subtype: Optional[str] = Field(None)
    parameters: Optional[Dict[str, str]] = Field(None)
    qualityValue: Optional[float] = Field(None)
    wildcardType: Optional[bool] = Field(None)
    wildcardSubtype: Optional[bool] = Field(None)
    subtypeSuffix: Optional[str] = Field(None)
    concrete: Optional[bool] = Field(None)
    charset: Optional[str] = Field(None)


Range = Dict[Any, Any]


class Occurrence(ProductionBaseModel):
    """An occurrence record representing a single biological event or observation."""

    key: int = Field(
        ..., description="Unique GBIF key for the occurrence.", examples=[2005380410]
    )
    datasetKey: UUID = Field(
        ...,
        description="The UUID of the GBIF dataset containing this occurrence.",
        examples=["13b70480-bd69-11dd-b15f-b8a03c50a862"],
    )
    publishingOrgKey: UUID = Field(
        ...,
        description="The UUID of the organization which publishes the dataset.",
        examples=["e2e717bf-551a-4917-bdc9-4fa0f342c530"],
    )
    networkKeys: Optional[List[UUID]] = Field(
        None,
        description="Any networks to which the dataset is registered.",
        examples=[["2b7c7b4f-4d4f-40d3-94de-c28b6fa054a6"]],
    )
    installationKey: Optional[UUID] = Field(
        None,
        description="The UUID of the technical installation that hosted the dataset.",
        examples=["17a83780-3060-4851-9d6f-029d5fcb81c9"],
    )
    hostingOrganizationKey: Optional[UUID] = Field(
        None,
        description="The UUID of the organization operating the technical installation.",
        examples=["fbca90e3-8aed-48b1-84e3-369afbd000ce"],
    )
    publishingCountry: Optional[str] = Field(
        None,
        description="The country of the organization publishing the dataset. (Full list at /v1/enumeration/country)",
        examples=["AD"],
    )
    protocol: ProtocolEnum = Field(
        ...,
        description="The technical protocol by which this occurrence was retrieved.",
        examples=["DWC_ARCHIVE"],
    )
    lastCrawled: Optional[datetime] = Field(
        None,
        description="The time this occurrence was last retrieved from the publisher's systems.",
    )
    lastParsed: Optional[datetime] = Field(
        None,
        description="The time this occurrence was last processed by GBIF's interpretation system.",
    )
    crawlId: Optional[int] = Field(
        None, description="The sequence number of the crawl attempt.", examples=[1]
    )
    projectId: Optional[str] = Field(
        None,
        description="The identifier for a project, often assigned by a funded programme.",
        examples=["bid-af2020-039-reg"],
    )
    programmeAcronym: Optional[str] = Field(
        None,
        description="The identifier for a programme which funded the digitization.",
        examples=["BID"],
    )
    extensions: Dict[str, List[Dict[str, str]]] = Field(
        ..., description="Verbatim Darwin Core Archive extension fields."
    )
    basisOfRecord: Optional[BasisOfRecordEnum] = Field(
        None,
        description="The specific nature of the data record.",
        examples=["PRESERVED_SPECIMEN"],
    )
    individualCount: Optional[int] = Field(
        None,
        description="The number of individuals present at the time of the Occurrence.",
    )
    occurrenceStatus: Optional[OccurrenceStatusEnum] = Field(
        None,
        description="A statement about the presence or absence of a Taxon at a Location.",
        examples=["PRESENT"],
    )
    sex: Optional[str] = Field(
        None, description="The sex of the biological individual(s).", examples=["MALE"]
    )
    lifeStage: Optional[str] = Field(
        None,
        description="The age class or life stage of the Organism(s).",
        examples=["Juvenile"],
    )
    establishmentMeans: Optional[str] = Field(
        None,
        description="Statement about whether an organism has been introduced by modern humans.",
        examples=["Native"],
    )
    degreeOfEstablishment: Optional[str] = Field(
        None,
        description="The degree to which an Organism survives, reproduces, and expands its range.",
        examples=["Invasive"],
    )
    pathway: Optional[str] = Field(
        None,
        description="The process by which an Organism came to be in a given place at a given time.",
        examples=["Agriculture"],
    )
    classifications: Optional[Dict[str, Classification]] = Field(
        None, description="The map of classifications associated with this occurrence."
    )
    taxonKey: Optional[int] = Field(
        None,
        description="A taxon key from the GBIF backbone for the most specific taxon.",
        deprecated=True,
        examples=[2476674],
    )
    kingdomKey: Optional[int] = Field(
        None,
        description="A taxon key from the GBIF backbone for the kingdom.",
        deprecated=True,
        examples=[5],
    )
    phylumKey: Optional[int] = Field(
        None,
        description="A taxon key from the GBIF backbone for the phylum.",
        deprecated=True,
        examples=[44],
    )
    classKey: Optional[int] = Field(
        None,
        description="A taxon key from the GBIF backbone for the class.",
        deprecated=True,
        examples=[212],
    )
    orderKey: Optional[int] = Field(
        None,
        description="A taxon key from the GBIF backbone for the order.",
        deprecated=True,
        examples=[1448],
    )
    familyKey: Optional[int] = Field(
        None,
        description="A taxon key from the GBIF backbone for the family.",
        deprecated=True,
        examples=[2405],
    )
    genusKey: Optional[int] = Field(
        None,
        description="A taxon key from the GBIF backbone for the genus.",
        deprecated=True,
        examples=[2877951],
    )
    subgenusKey: Optional[int] = Field(
        None,
        description="A taxon key from the GBIF backbone for the subgenus.",
        deprecated=True,
    )
    speciesKey: Optional[int] = Field(
        None,
        description="A taxon key from the GBIF backbone for the species.",
        deprecated=True,
        examples=[2476674],
    )
    acceptedTaxonKey: Optional[int] = Field(
        None,
        description="A taxon key from the GBIF backbone for the accepted taxon.",
        deprecated=True,
        examples=[2476674],
    )
    scientificName: Optional[str] = Field(
        None,
        description="The scientific name (including authorship) for the taxon from the GBIF backbone.",
        examples=["Quercus robur L."],
    )
    scientificNameAuthorship: Optional[str] = Field(
        None,
        description="The scientific name authorship for the taxon from the GBIF backbone.",
    )
    acceptedScientificName: Optional[str] = Field(
        None,
        description="The accepted scientific name (including authorship) for the taxon from the GBIF backbone.",
    )
    kingdom: Optional[str] = Field(
        None, description="The kingdom name from the GBIF backbone."
    )
    phylum: Optional[str] = Field(
        None, description="The phylum name from the GBIF backbone."
    )
    order: Optional[str] = Field(
        None, description="The order name from the GBIF backbone."
    )
    family: Optional[str] = Field(
        None, description="The family name from the GBIF backbone."
    )
    genus: Optional[str] = Field(
        None, description="The genus name from the GBIF backbone."
    )
    subgenus: Optional[str] = Field(
        None, description="The subgenus name from the GBIF backbone."
    )
    species: Optional[str] = Field(
        None, description="The species name from the GBIF backbone."
    )
    genericName: Optional[str] = Field(
        None, description="The genus name part of the scientific name."
    )
    specificEpithet: Optional[str] = Field(
        None, description="The specific name part of the scientific name."
    )
    infraspecificEpithet: Optional[str] = Field(
        None, description="The infraspecific name part of the scientific name."
    )
    taxonRank: Optional[TaxonRankEnum] = Field(
        None,
        description="The taxonomic rank of the most specific name in the scientificName.",
    )
    taxonomicStatus: Optional[TaxonomicStatusEnum] = Field(
        None,
        description="The status of the use of the scientificName as a label for a taxon.",
        examples=["SYNONYM"],
    )
    iucnRedListCategory: Optional[str] = Field(
        None, description="The IUCN Red List Category of the taxon.", examples=["EX"]
    )
    dateIdentified: Optional[datetime] = Field(
        None,
        description="The date on which the subject was determined as representing the Taxon.",
    )
    decimalLatitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="The geographic latitude (in decimal degrees, WGS84). Must be between -90 and 90.",
        examples=[40.5],
    )
    decimalLongitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="The geographic longitude (in decimal degrees, WGS84). Must be between -180 and 180.",
        examples=[-120],
    )
    coordinatePrecision: Optional[float] = Field(
        None,
        description="A decimal representation of the precision of the coordinates.",
    )
    coordinateUncertaintyInMeters: Optional[float] = Field(
        None,
        description="The horizontal distance (in metres) from the given coordinates describing the smallest circle containing the whole Location.",
        examples=[500.0],
    )
    coordinateAccuracy: Optional[float] = Field(
        None, description="Deprecated. Always null.", deprecated=True
    )
    elevation: Optional[float] = Field(
        None,
        description="Elevation (altitude) in metres above sea level.",
        examples=[1000.0],
    )
    elevationAccuracy: Optional[float] = Field(
        None, description="The potential error associated with the elevation."
    )
    depth: Optional[float] = Field(
        None, description="Depth in metres below sea level.", examples=[10.0]
    )
    depthAccuracy: Optional[float] = Field(
        None, description="The potential error associated with the depth."
    )
    continent: Optional[ContinentEnum] = Field(
        None,
        description="The continent in which the occurrence was recorded.",
        examples=["EUROPE"],
    )
    stateProvince: Optional[str] = Field(
        None,
        description="The name of the next-smaller administrative region than country.",
        examples=["Leicestershire"],
    )
    gadm: Gadm = Field(
        ..., description="The administrative divisions according to the GADM database."
    )
    waterBody: Optional[str] = Field(
        None,
        description="The name of the water body in which the Location occurs.",
        examples=["Lake Michigan"],
    )
    distanceFromCentroidInMeters: Optional[float] = Field(
        None,
        description="The distance in metres of the occurrence from a known georeferencing centroid.",
        examples=[500.0],
    )
    higherGeography: Optional[str] = Field(
        None,
        description="A list of geographic names less specific than the locality term.",
        examples=["Argentina"],
    )
    georeferencedBy: Optional[str] = Field(
        None,
        description="A list of names of people, groups, or organizations who determined the georeference.",
        examples=["Brad Millen"],
    )
    year: Optional[int] = Field(
        None,
        le=datetime.now().year + 1,
        description="The four-digit year in which the event occurred.",
        examples=[1998],
    )
    month: Optional[int] = Field(
        None,
        ge=1,
        le=12,
        description="The integer month in which the Event occurred (1-12).",
        examples=[5],
    )
    day: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="The integer day of the month on which the Event occurred (1-31).",
        examples=[15],
    )
    eventDate: Optional[IsoDateInterval] = Field(
        None,
        description="The date-time during which an Event occurred.",
        examples=["2001-06-30T00:00:00"],
    )
    startDayOfYear: Optional[int] = Field(
        None,
        ge=1,
        le=366,
        description="The earliest integer day of the year on which the Event occurred (1-366).",
        examples=[5],
    )
    endDayOfYear: Optional[int] = Field(
        None,
        ge=1,
        le=366,
        description="The latest integer day of the year on which the Event occurred (1-366).",
        examples=[6],
    )
    typeStatus: Optional[str] = Field(
        None,
        description="A list of nomenclatural types applied to the occurrence.",
        examples=["HOLOTYPE"],
    )
    typifiedName: Optional[str] = Field(
        None, description="The scientific name that is based on the type specimen."
    )
    issues: List[str] = Field(
        ...,
        description="A list of interpretation issues found. For a full list of possible values, see the GBIF OccurrenceIssue enumeration.",
    )
    modified: Optional[datetime] = Field(
        None,
        description="The most recent date-time on which the occurrence was changed, according to the publisher.",
        examples=["2023-02-20T00:00:00"],
    )
    lastInterpreted: Optional[datetime] = Field(
        None,
        description="The time this occurrence was last processed by GBIF's interpretation system.",
        examples=["2023-02-01T00:00:00"],
    )
    references: Optional[str] = Field(
        None,
        description="A related resource that is referenced, cited, or otherwise pointed to.",
    )
    license: LicenseEnum = Field(
        ...,
        description="A legal document giving official permission to do something with the occurrence.",
        examples=["CC0_1_0"],
    )
    organismQuantity: Optional[float] = Field(
        None,
        description="A number or enumeration value for the quantity of organisms.",
        examples=[1.0],
    )
    organismQuantityType: Optional[str] = Field(
        None,
        description="The type of quantification system used for the quantity of organisms.",
        examples=["individuals"],
    )
    sampleSizeUnit: Optional[str] = Field(
        None,
        description="The unit of measurement of the size of a sample in a sampling event.",
        examples=["hectares"],
    )
    sampleSizeValue: Optional[float] = Field(
        None,
        description="A numeric value for a measurement of the size of a sample.",
        examples=[50.5],
    )
    relativeOrganismQuantity: Optional[float] = Field(
        None, description="The relative measurement of the quantity of the organism."
    )
    isSequenced: Optional[bool] = Field(
        None,
        description="Flag indicating if associated sequence information exists.",
        examples=[True],
    )
    associatedSequences: Optional[str] = Field(
        None,
        description="A list of identifiers of genetic sequence information.",
        examples=["http://www.ncbi.nlm.nih.gov/nuccore/U34853.1"],
    )
    identifiers: List[Identifier] = Field(
        ..., description="Alternative identifiers for the occurrence."
    )
    media: List[MediaObject] = Field(
        ..., description="Multimedia related to the occurrence."
    )
    facts: List[MeasurementOrFact] = Field(
        ..., description="Measurements or facts about the occurrence."
    )
    relations: List[OccurrenceRelation] = Field(
        ..., description="Relationships between occurrences."
    )
    institutionKey: Optional[str] = Field(
        None,
        description="Experimental. The UUID of the institution holding the specimen, from GRSciColl.",
        examples=["fa252605-26f6-426c-9892-94d071c2c77f"],
    )
    collectionKey: Optional[str] = Field(
        None,
        description="Experimental. The UUID of the collection containing the specimen, from GRSciColl.",
        examples=["dceb8d52-094c-4c2c-8960-75e0097c6861"],
    )
    isInCluster: Optional[bool] = Field(
        None,
        description="Experimental. Whether the occurrence belongs to a machine-calculated cluster of probable duplicates.",
        examples=[True],
    )
    datasetID: Optional[str] = Field(
        None,
        description="An identifier for the set of data.",
        examples=["https://doi.org/10.1594/PANGAEA.315492"],
    )
    datasetName: Optional[str] = Field(
        None,
        description="The name identifying the data set from which the record was derived.",
    )
    otherCatalogNumbers: Optional[str] = Field(
        None,
        description="A list of previous or alternate fully qualified catalogue numbers.",
    )
    earliestEonOrLowestEonothem: Optional[str] = Field(
        None,
        description="The full name of the earliest possible geochronologic eon.",
        examples=["Proterozoic"],
    )
    latestEonOrHighestEonothem: Optional[str] = Field(
        None,
        description="The full name of the latest possible geochronologic eon.",
        examples=["Proterozoic"],
    )
    earliestEraOrLowestErathem: Optional[str] = Field(
        None,
        description="The full name of the earliest possible geochronologic era.",
        examples=["Mesozoic"],
    )
    latestEraOrHighestErathem: Optional[str] = Field(
        None,
        description="The full name of the latest possible geochronologic era.",
        examples=["Cenozoic"],
    )
    earliestPeriodOrLowestSystem: Optional[str] = Field(
        None,
        description="The full name of the earliest possible geochronologic period.",
        examples=["Neogene"],
    )
    latestPeriodOrHighestSystem: Optional[str] = Field(
        None,
        description="The full name of the latest possible geochronologic period.",
        examples=["Neogene"],
    )
    earliestEpochOrLowestSeries: Optional[str] = Field(
        None,
        description="The full name of the earliest possible geochronologic epoch.",
        examples=["Holocene"],
    )
    latestEpochOrHighestSeries: Optional[str] = Field(
        None,
        description="The full name of the latest possible geochronologic epoch.",
        examples=["Pleistocene"],
    )
    earliestAgeOrLowestStage: Optional[str] = Field(
        None,
        description="The full name of the earliest possible geochronologic age.",
        examples=["Skullrockian"],
    )
    latestAgeOrHighestStage: Optional[str] = Field(
        None,
        description="The full name of the latest possible geochronologic age.",
        examples=["Boreal"],
    )
    lowestBiostratigraphicZone: Optional[str] = Field(
        None,
        description="The full name of the lowest possible geological biostratigraphic zone.",
        examples=["Maastrichtian"],
    )
    highestBiostratigraphicZone: Optional[str] = Field(
        None,
        description="The full name of the highest possible geological biostratigraphic zone.",
        examples=["Blancan"],
    )
    group: Optional[str] = Field(
        None,
        description="The full name of the lithostratigraphic group.",
        examples=["Bathurst"],
    )
    formation: Optional[str] = Field(
        None,
        description="The full name of the lithostratigraphic formation.",
        examples=["Notch Peak Formation"],
    )
    member: Optional[str] = Field(
        None,
        description="The full name of the lithostratigraphic member.",
        examples=["Lava Dam Member"],
    )
    bed: Optional[str] = Field(
        None,
        description="The full name of the lithostratigraphic bed.",
        examples=["Harlem coal"],
    )
    recordedBy: Optional[str] = Field(
        None,
        description="A person, group, or organization responsible for recording the original occurrence.",
        examples=["MiljoStyrelsen"],
    )
    identifiedBy: Optional[str] = Field(
        None,
        description="A list of names of people, groups, or organizations who assigned the Taxon to the occurrence.",
        examples=["Allison"],
    )
    preparations: Optional[str] = Field(
        None,
        description="A preparation or preservation method for a specimen.",
        examples=["pinned"],
    )
    samplingProtocol: Optional[str] = Field(
        None,
        description="The methods or protocols used during an Event.",
        examples=["malaise trap"],
    )
    dnaSequenceID: Optional[List[str]] = Field(
        None, description="Experimental. The DNA sequence ID of an occurrence."
    )
    geodeticDatum: Optional[str] = Field(
        None,
        description="The geodetic datum for the interpreted decimal coordinates (always WGS84 if reprojected).",
    )
    class_name: Optional[str] = Field(
        None, alias="class", description="The class name from the GBIF backbone."
    )
    countryCode: Optional[str] = Field(
        None,
        description="The 2-letter country code of the country in which the occurrence was recorded. (Full list at /v1/enumeration/country)",
        examples=["AF"],
    )
    recordedByIDs: List[AgentIdentifier] = Field(
        ...,
        description="A list of globally unique identifiers for the person, people, groups, or organizations responsible for recording the original Occurrence.",
    )
    identifiedByIDs: List[AgentIdentifier] = Field(
        ...,
        description="A list of globally unique identifiers for the person, people, groups, or organizations responsible for assigning the Taxon to the occurrence.",
    )
    gbifRegion: Optional[GBIFRegionEnum] = Field(
        None, description="GBIF region based on country code.", examples=["AFRICA"]
    )
    country: Optional[str] = Field(
        None,
        description="The title of the country in which the occurrence was recorded.",
    )
    publishedByGbifRegion: Optional[GBIFRegionEnum] = Field(
        None,
        description="GBIF region based on the owning organization's country.",
        examples=["AFRICA"],
    )


class SearchResponseOccurrenceOccurrenceSearchParameter(ProductionBaseModel):
    """The response wrapper for an occurrence search."""

    endOfRecords: Optional[bool] = Field(
        None, description="True if this page of search results is the final page."
    )
    count: Optional[int] = Field(
        None, description="The total number of records returned by the search."
    )
    results: Optional[List[Occurrence]] = Field(
        None, description="The list of occurrence search results."
    )
    facets: Optional[List[FacetOccurrenceSearchParameter]] = Field(
        None, description="The resulting facets of a search operation."
    )


# Rebuild models to resolve forward references in recursive predicate models
for model in [
    ConjunctionPredicate,
    DisjunctionPredicate,
    NotPredicate,
    OccurrencePredicateSearchRequest,
]:
    model.model_rebuild()
