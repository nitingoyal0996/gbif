from typing import List, Optional
from uuid import UUID
from pydantic import Field, field_validator

from .base import ProductionBaseModel

from .enums.occurence_parameters import (
    BasisOfRecordEnum,
    ContinentEnum,
    OccurrenceStatusEnum,
    LicenseEnum,
    MediaObjectTypeEnum,
)

from .enums.species_parameters import (
    TaxonomicRankEnum,
    TaxonomicStatusEnum,
    HabitatEnum,
    ThreatStatusEnum,
    NameTypeEnum,
    OriginEnum,
    TypeStatusEnum,
    NomenclaturalStatusEnum,
    IssueEnum,
)


class GBIFOccurrenceBaseParams(ProductionBaseModel):
    """Base parameters for GBIF occurrence operations - contains all common search and filter parameters"""

    # Core search parameters
    scientificName: Optional[List[str]] = Field(
        None,
        description="Only use this parameter if the user has provided a scientific name. A scientific name from the GBIF backbone or the specified checklist. All included and synonym taxa are included in the search. Under the hood a call to the species match service is done first to retrieve a taxonKey. Only unique scientific names will return results, homonyms (many monomials) return nothing! Consider to use the taxonKey parameter instead and the species match service directly.",
        examples=[
            ["Quercus robur"],
            ["Homo sapiens", "Canis lupus"],
            ["Puma concolor"],
        ],
    )

    q: Optional[str] = Field(
        None,
        description="Simple full-text search parameter. The value for this parameter can be a simple word or a phrase. Wildcards are not supported. Full-text search fields include: title, keyword, country, publishing country, publishing organization title, hosting organization title, and description.",
        examples=["plant", "bird observation", "mammal specimen"],
    )

    occurrenceId: Optional[List[str]] = Field(
        None,
        description="A globally unique identifier for the occurrence record as provided by the publisher.",
        examples=[["URN:catalog:UWBM:Bird:126493"], ["2005380410", "9876543210"]],
    )

    taxonKey: Optional[List[int]] = Field(
        None,
        description="A taxon key from the GBIF backbone or the specified checklist. All included (child) and synonym taxa are included in the search, so a search for Aves with taxonKey=212 will match all birds, no matter which species.",
        examples=[[2476674], [2877951, 212], [44, 212, 1448]],
    )

    datasetKey: Optional[List[UUID]] = Field(
        None,
        description="The occurrence dataset key (a UUID).",
        examples=[
            ["13b70480-bd69-11dd-b15f-b8a03c50a862"],
            ["e2e717bf-551a-4917-bdc9-4fa0f342c530"],
        ],
    )

    basisOfRecord: Optional[List[BasisOfRecordEnum]] = Field(
        None,
        description="Basis of record, as defined in our BasisOfRecord vocabulary. The values of the Darwin Core term Basis of Record which can apply to occurrences.",
        examples=[
            [BasisOfRecordEnum.PRESERVED_SPECIMEN],
            [BasisOfRecordEnum.HUMAN_OBSERVATION, BasisOfRecordEnum.OBSERVATION],
            [BasisOfRecordEnum.FOSSIL_SPECIMEN, BasisOfRecordEnum.LIVING_SPECIMEN],
        ],
    )

    catalogNumber: Optional[List[str]] = Field(
        None,
        description="An identifier of any form assigned by the source within a physical collection or digital dataset for the record which may not be unique, but should be fairly unique in combination with the institution and collection code.",
        examples=[["K001275042"], ["12345", "67890"]],
    )

    # Geographic filters
    country: Optional[List[str]] = Field(
        None,
        description="The 2-letter country code (as per ISO-3166-1) of the country in which the occurrence was recorded.",
        examples=[["US"], ["GB", "FR", "DE"], ["AF", "ZA", "KE"]],
    )

    continent: Optional[List[ContinentEnum]] = Field(
        None,
        description="Continent, as defined in our Continent vocabulary. The continent, based on a 7 continent model described on Wikipedia and the World Geographical Scheme for Recording Plant Distributions (WGSRPD). This splits the Americas into North and South America with North America including the Caribbean (except Trinidad and Tobago) and reaching down and including Panama.",
        examples=[
            [ContinentEnum.EUROPE],
            [ContinentEnum.NORTH_AMERICA, ContinentEnum.SOUTH_AMERICA],
            [ContinentEnum.AFRICA, ContinentEnum.ASIA],
        ],
    )

    decimalLatitude: Optional[str] = Field(
        None,
        description="Latitude in decimal degrees between -90° and 90° based on WGS 84. Supports range queries.",
        examples=["40.5,45", "-90,90", "30,50"],
    )

    decimalLongitude: Optional[str] = Field(
        None,
        description="Longitude in decimals between -180 and 180 based on WGS 84. Supports range queries.",
        examples=["-120,-95.5", "-180,180", "-100,-50"],
    )

    hasCoordinate: Optional[bool] = Field(
        None,
        description="Limits searches to occurrence records which contain a value in both latitude and longitude (i.e. hasCoordinate=true limits to occurrence records with coordinate values and hasCoordinate=false limits to occurrence records without coordinate values).",
        examples=[True, False],
    )

    hasGeospatialIssue: Optional[bool] = Field(
        None,
        description="Includes/excludes occurrence records which contain spatial issues (as determined in our record interpretation), i.e. hasGeospatialIssue=true returns only those records with spatial issues while hasGeospatialIssue=false includes only records without spatial issues. The absence of this parameter returns any record with or without spatial issues.",
        examples=[True, False],
    )

    # Temporal filters
    year: Optional[str] = Field(
        None,
        description="The 4 digit year. A year of 98 will be interpreted as AD 98. Supports range queries using comma-separated values. For instance: year='2020,2023' will return all records from 2020 and 2023 (not including 2021 and 2022). To express a range 'from YYY1 to YYY3', use the format 'YYY1,YYY3'.",
        examples=["2020", "2010,2020", "1998,2005"],
    )

    month: Optional[str] = Field(
        None,
        description="The month of the year, starting with 1 for January. Supports range queries. For instance: month='5,12' will return all records from May to December.",
        examples=["5", "1,12", "3,9"],
    )

    eventDate: Optional[List[str]] = Field(
        None,
        description="Occurrence date in ISO 8601 format: yyyy, yyyy-MM or yyyy-MM-dd. Supports range queries. For instance: eventDate='2020,2023' will return all records from 2020 and 2023.",
        examples=[["2020"], ["2020-01", "2020-12"], ["2000,2001-06-30"]],
    )

    # Taxonomic filters
    kingdomKey: Optional[List[int]] = Field(
        None, description="Kingdom classification key.", examples=[[5], [1, 2, 3]]
    )

    phylumKey: Optional[List[int]] = Field(
        None, description="Phylum classification key.", examples=[[44], [1, 2, 3]]
    )

    classKey: Optional[List[int]] = Field(
        None, description="Class classification key.", examples=[[212], [1, 2, 3]]
    )

    orderKey: Optional[List[int]] = Field(
        None, description="Order classification key.", examples=[[1448], [1, 2, 3]]
    )

    familyKey: Optional[List[int]] = Field(
        None, description="Family classification key.", examples=[[2405], [1, 2, 3]]
    )

    genusKey: Optional[List[int]] = Field(
        None, description="Genus classification key.", examples=[[2877951], [1, 2, 3]]
    )

    speciesKey: Optional[List[int]] = Field(
        None, description="Species classification key.", examples=[[2476674], [1, 2, 3]]
    )

    # Additional filters
    occurrenceStatus: Optional[OccurrenceStatusEnum] = Field(
        None,
        description="Either PRESENT or ABSENT; the presence or absence of the occurrence. A statement about the presence or absence of a Taxon at a Location.",
        examples=[OccurrenceStatusEnum.PRESENT, OccurrenceStatusEnum.ABSENT],
    )

    license: Optional[List[LicenseEnum]] = Field(
        None,
        description="The licence applied to the dataset or record by the publisher.",
        examples=[
            [LicenseEnum.CC0_1_0],
            [LicenseEnum.CC_BY_4_0, LicenseEnum.CC_BY_NC_4_0],
        ],
    )

    institutionCode: Optional[List[str]] = Field(
        None,
        description="An identifier of any form assigned by the source to identify the institution the record belongs to. Not guaranteed to be unique.",
        examples=[["K"], ["USNM", "BMNH"]],
    )

    collectionCode: Optional[List[str]] = Field(
        None,
        description="An identifier of any form assigned by the source to identify the physical collection or digital dataset uniquely within the context of an institution.",
        examples=[["F"], ["BIRD", "MAMMAL"]],
    )

    recordedBy: Optional[List[str]] = Field(
        None,
        description="The person who recorded the occurrence.",
        examples=[["MiljoStyrelsen"], ["John Smith", "Jane Doe"]],
    )

    identifiedBy: Optional[List[str]] = Field(
        None,
        description="The person who provided the taxonomic identification of the occurrence.",
        examples=[["Allison"], ["Dr. Smith", "Prof. Johnson"]],
    )

    typeStatus: Optional[List[TypeStatusEnum]] = Field(
        None,
        description="Nomenclatural type (type status, typified scientific name, publication) applied to the subject.",
        examples=[
            [TypeStatusEnum.HOLOTYPE],
            [TypeStatusEnum.PARATYPE, TypeStatusEnum.SYNTYPE],
            [TypeStatusEnum.LECTOTYPE, TypeStatusEnum.NEOTYPE],
        ],
    )

    isSequenced: Optional[bool] = Field(
        None,
        description="Flag occurrence when associated sequences exists.",
        examples=[True, False],
    )

    mediaType: Optional[List[MediaObjectTypeEnum]] = Field(
        None,
        description="The kind of multimedia associated with an occurrence as defined in our MediaType enumeration.",
        examples=[
            [MediaObjectTypeEnum.StillImage],
            [MediaObjectTypeEnum.MovingImage, MediaObjectTypeEnum.Sound],
            [MediaObjectTypeEnum.InteractiveResource],
        ],
    )

    # Pagination parameters
    limit: Optional[int] = Field(
        100,
        ge=0,
        le=300,
        description="Controls the number of results in the page. Using too high a value will be overwritten with the maximum threshold, which is 300 for this service. A limit of 0 will return no record data.",
    )

    offset: Optional[int] = Field(
        0,
        ge=0,
        le=100000,
        description="Determines the offset for the search results. A limit of 20 and offset of 40 will get the third page of 20 results. This service has a maximum offset of 100,000.",
    )

    @field_validator("decimalLatitude")
    @classmethod
    def validate_latitude(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Handle range format (e.g., "40.5,45")
        parts = v.split(",")
        for part in parts:
            try:
                lat = float(part.strip())
                if lat < -90 or lat > 90:
                    raise ValueError(
                        f"Latitude must be between -90 and 90 degrees, got {lat}"
                    )
            except ValueError as e:
                if "must be between" not in str(e):
                    raise ValueError(f"Invalid latitude format: {part}")
                raise
        return v

    @field_validator("decimalLongitude")
    @classmethod
    def validate_longitude(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Handle range format (e.g., "-120,-95.5")
        parts = v.split(",")
        for part in parts:
            try:
                lon = float(part.strip())
                if lon < -180 or lon > 180:
                    raise ValueError(
                        f"Longitude must be between -180 and 180 degrees, got {lon}"
                    )
            except ValueError as e:
                if "must be between" not in str(e):
                    raise ValueError(f"Invalid longitude format: {part}")
                raise
        return v


class GBIFOccurrenceSearchParams(GBIFOccurrenceBaseParams):
    """Parameters for GBIF occurrence search - matches API structure"""

    pass


class GBIFOccurrenceFacetsParams(GBIFOccurrenceBaseParams):
    """Parameters for GBIF occurrence faceting - extends search params with faceting options"""

    # Faceting parameters
    facet: List[str] = Field(
        ...,
        description="A facet name used to retrieve the most frequent values for a field. Facets are allowed for all search parameters except geometry and geoDistance. This parameter may be repeated to request multiple facets. Note terms not available for searching are not available for faceting.",
        examples=[
            ["scientificName"],
            ["country", "year"],
            ["basisOfRecord", "kingdom"],
            ["datasetKey", "publishingCountry"],
        ],
    )

    facetMincount: Optional[int] = Field(
        1,
        ge=1,
        description="Used in combination with the facet parameter. Set facetMincount={#} to exclude facets with a count less than {#}.",
        examples=[100, 1000, 10000],
    )

    facetMultiselect: Optional[bool] = Field(
        False, description="Allow multi-select faceting"
    )

    # Override limit default for faceting (0 for facets only)
    limit: Optional[int] = Field(
        0, ge=0, le=300, description="Number of results per page (0 for facets only)"
    )


class GBIFSpeciesSearchParams(ProductionBaseModel):
    """Parameters for GBIF species search - full text search over name usages covering scientific and vernacular names, species descriptions, distribution and classification data"""

    # Core search parameters
    q: Optional[str] = Field(
        None,
        description="Simple full text search parameter covering scientific and vernacular names, species descriptions, distribution and entire classification. The value can be a simple word or phrase. Wildcards are not supported. Results are ordered by relevance.",
        examples=[
            "Puma concolor",
            "jaguar",
            "Quercus",
            "oak tree",
            "Panthera tigris",
            "endangered cats",
        ],
    )

    datasetKey: Optional[str] = Field(
        None,
        description="A UUID of a checklist dataset to limit the search scope. Useful for searching within specific taxonomic authorities or regional checklists.",
        examples=["d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"],  # GBIF Backbone Taxonomy
    )

    constituentKey: Optional[str] = Field(
        None,
        description="The (sub)dataset constituent key as a UUID. Useful to query larger assembled datasets such as the GBIF Backbone or the Catalogue of Life for specific constituent parts.",
        examples=["7ce8aef0-9e92-11dc-8738-b8a03c50a862"],
    )

    rank: Optional[TaxonomicRankEnum] = Field(
        None,
        description="Filters by taxonomic rank as defined in the GBIF rank enumeration. Helps narrow results to specific taxonomic levels.",
        examples=[
            TaxonomicRankEnum.SPECIES,
            TaxonomicRankEnum.GENUS,
            TaxonomicRankEnum.FAMILY,
            TaxonomicRankEnum.ORDER,
        ],
    )

    higherTaxonKey: Optional[int] = Field(
        None,
        description="Filters by any of the higher Linnean rank keys within the respective checklist. Note this searches within the specific checklist, not across all NUB keys. Useful for finding all taxa under a specific higher taxon.",
        examples=[212, 44, 1448, 2405],  # Example keys for different higher taxa
    )

    status: Optional[TaxonomicStatusEnum] = Field(
        None,
        description="Filters by the taxonomic status to distinguish between accepted names, synonyms, and doubtful names. Essential for taxonomic research and data quality control.",
        examples=[
            TaxonomicStatusEnum.ACCEPTED,
            TaxonomicStatusEnum.SYNONYM,
            TaxonomicStatusEnum.DOUBTFUL,
        ],
    )

    isExtinct: Optional[bool] = Field(
        None,
        description="Filters by extinction status. True returns only extinct taxa, False returns only extant taxa, None returns both.",
        examples=[True, False],
    )

    habitat: Optional[HabitatEnum] = Field(
        None,
        description="Filters by major habitat classification. Currently supports three major biomes as defined in the GBIF habitat enumeration.",
        examples=[HabitatEnum.MARINE, HabitatEnum.FRESHWATER, HabitatEnum.TERRESTRIAL],
    )

    threat: Optional[ThreatStatusEnum] = Field(
        None,
        description="Filters by IUCN Red List threat status categories. Useful for conservation research and identifying species of conservation concern.",
        examples=[
            ThreatStatusEnum.CRITICALLY_ENDANGERED,
            ThreatStatusEnum.ENDANGERED,
            ThreatStatusEnum.VULNERABLE,
            ThreatStatusEnum.NEAR_THREATENED,
            ThreatStatusEnum.LEAST_CONCERN,
            ThreatStatusEnum.DATA_DEFICIENT,
        ],
    )

    nameType: Optional[NameTypeEnum] = Field(
        None,
        description="Filters by the type of name string as classified by GBIF's name parser. Helps distinguish between different categories of taxonomic names.",
        examples=[
            NameTypeEnum.SCIENTIFIC,
            NameTypeEnum.VIRUS,
            NameTypeEnum.HYBRID,
            NameTypeEnum.CULTIVAR,
            NameTypeEnum.INFORMAL,
        ],
    )

    nomenclaturalStatus: Optional[NomenclaturalStatusEnum] = Field(
        None,
        description="Filters by nomenclatural status according to the relevant nomenclatural code. Important for understanding the validity and legitimacy of scientific names.",
        examples=[
            NomenclaturalStatusEnum.LEGITIMATE,
            NomenclaturalStatusEnum.VALIDLY_PUBLISHED,
            NomenclaturalStatusEnum.NEW_COMBINATION,
            NomenclaturalStatusEnum.REPLACEMENT,
            NomenclaturalStatusEnum.CONSERVED,
            NomenclaturalStatusEnum.ILLEGITIMATE,
            NomenclaturalStatusEnum.INVALID,
            NomenclaturalStatusEnum.REJECTED,
        ],
    )

    origin: Optional[OriginEnum] = Field(
        None,
        description="Filters for name usages with a specific origin, indicating how the name usage was created or derived during data processing.",
        examples=[
            OriginEnum.SOURCE,
            OriginEnum.DENORMED_CLASSIFICATION,
            OriginEnum.VERBATIM_PARENT,
            OriginEnum.AUTONYM,
        ],
    )

    issue: Optional[IssueEnum] = Field(
        None,
        description="Filters by specific data quality issues identified during GBIF's indexing process. Useful for data quality assessment and cleanup.",
        examples=[
            IssueEnum.BACKBONE_MATCH_NONE,
            IssueEnum.BACKBONE_MATCH_FUZZY,
            IssueEnum.ACCEPTED_NAME_MISSING,
            IssueEnum.CLASSIFICATION_RANK_ORDER_INVALID,
            IssueEnum.TAXONOMIC_STATUS_MISMATCH,
        ],
    )

    hl: Optional[bool] = Field(
        None,
        description="Enable search term highlighting in results. When set to true, matching terms in fulltext search fields will be wrapped in emphasis tags with class 'gbifHl' for visual highlighting.",
        examples=[True, False],
    )

    # Pagination parameters
    limit: Optional[int] = Field(
        20,
        ge=0,
        le=1000,
        description="Controls the number of results returned per page. Higher values may be capped by service limits. Use with offset for pagination through large result sets.",
        examples=[10, 20, 50, 100],
    )

    offset: Optional[int] = Field(
        0,
        ge=0,
        description="Determines the starting point for search results. Use with limit for pagination. For example, limit=20 and offset=40 returns the third page of 20 results.",
        examples=[0, 20, 100, 500],
    )


class GBIFSpeciesFacetsParams(GBIFSpeciesSearchParams):
    """Parameters for GBIF species faceting - extends species search params with required faceting options for counting and statistical analysis"""

    facet: Optional[List[str]] = Field(
        None,
        description="Facet field names for retrieving frequency counts of field values. Useful for analyzing result distributions and building filter interfaces. Can be repeated for multiple facets.",
        examples=[
            ["rank"],
            ["status", "habitat"],
            ["nameType", "threat"],
            ["rank", "status", "habitat"],
            ["datasetKey", "constituentKey"],
        ],
    )

    facetMincount: Optional[int] = Field(
        None,
        ge=1,
        description="Minimum count threshold for facet values. Excludes facet values with counts below this threshold to reduce noise in facet results.",
        examples=[1, 10, 100, 1000],
    )

    facetMultiselect: Optional[bool] = Field(
        None,
        description="When enabled, facet counts include values that are not currently filtered, allowing for multi-select filter interfaces with accurate counts.",
        examples=[True, False],
    )

    facetLimit: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum number of facet values to return per facet field. Use with facetOffset for paginating through large facet result sets.",
        examples=[10, 50, 100],
    )

    facetOffset: Optional[int] = Field(
        None,
        ge=0,
        description="Starting offset for facet value results. Use with facetLimit for paginating through facet values when there are many distinct values.",
        examples=[0, 50, 100],
    )


class GBIFSpeciesTaxonomicParams(ProductionBaseModel):
    """Parameters for GBIF species taxonomic information - retrieves comprehensive taxonomic data for a specific species"""

    # Required parameter - enforced usageKey
    usageKey: int = Field(
        ...,
        description="The GBIF usage key (taxon key) for the species. This is a required parameter that uniquely identifies the species in the GBIF backbone.",
        examples=[5231190, 2476674, 2877951],
    )

    # Optional parameters for controlling data retrieval
    includeSynonyms: Optional[bool] = Field(
        True,
        description="Whether to include synonyms in the response. Synonyms are alternative scientific names for the same taxon.",
        examples=[True, False],
    )

    includeChildren: Optional[bool] = Field(
        True,
        description="Whether to include child taxa (subspecies, varieties, etc.) in the response.",
        examples=[True, False],
    )

    includeParents: Optional[bool] = Field(
        True,
        description="Whether to include the complete taxonomic hierarchy (parents) in the response.",
        examples=[True, False],
    )

    language: Optional[str] = Field(
        "en",
        description="Language code for vernacular names and descriptions. Uses ISO 639-1 two-letter codes.",
        examples=["en", "es", "fr", "de", "zh"],
    )

    # Pagination for endpoints that support it
    limit: Optional[int] = Field(
        20,
        ge=1,
        le=100,
        description="Maximum number of results to return for paginated endpoints (synonyms, children, etc.).",
        examples=[10, 20, 50, 100],
    )

    offset: Optional[int] = Field(
        0,
        ge=0,
        description="Offset for pagination in paginated endpoints.",
        examples=[0, 20, 40],
    )
