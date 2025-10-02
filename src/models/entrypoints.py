from typing import List, Optional
from uuid import UUID
from pydantic import Field, field_validator

from .base import ProductionBaseModel

from .enums.occurence_parameters import (
    BasisOfRecordEnum,
    ContinentEnum,
    GbifRegionEnum,
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
    QueryFieldEnum,
)

from .enums.registry_parameters import (
    DatasetTypeEnum,
    DatasetSubtypeEnum,
    EndpointTypeEnum,
    ContinentEnum,
    LicenseEnum,
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

    acceptedTaxonKey: Optional[List[int]] = Field(
        None,
        description="A taxon key from the GBIF backbone or the specified checklist (see checklistKey parameter). Only synonym taxa are included in the search, so a search for Aves with acceptedTaxonKey=212 (i.e. /occurrence/search?taxonKey=212) will match occurrences identified as birds, but not any known family, genus or species of bird. Parameter may be repeated.",
        examples=[[2476674]],
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

    q: Optional[str] = Field(
        None,
        description="Simple full-text search parameter. The value for this parameter can be a simple word or a phrase. Wildcards are not supported",
        examples=["mammal", "Quercus robur"],
    )

    # DWCA extension parameters
    dwcaExtension: Optional[List[str]] = Field(
        None,
        description="A known Darwin Core Archive extension RowType. Limits the search to occurrences which have this extension, although they will not necessarily have any useful data recorded using the extension. Parameter may be repeated.",
        examples=[["http://rs.tdwg.org/ac/terms/Multimedia"]],
    )

    earliestEonOrLowestEonothem: Optional[List[str]] = Field(
        None,
        description="The full name of the earliest possible geochronologic era or lowest chronostratigraphic erathem attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
        examples=[["Mesozoic"]],
    )

    earliestEraOrLowestErathem: Optional[List[str]] = Field(
        None,
        description='The full name of the latest possible geochronologic eon or highest chrono-stratigraphic eonothem or the informal name ("Precambrian") attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.',
        examples=[["Proterozoic"]],
    )

    earliestPeriodOrLowestSystem: Optional[List[str]] = Field(
        None,
        description="The full name of the earliest possible geochronologic period or lowest chronostratigraphic system attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
        examples=[["Neogene"]],
    )

    earliestEpochOrLowestSeries: Optional[List[str]] = Field(
        None,
        description="The full name of the earliest possible geochronologic epoch or lowest chronostratigraphic series attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
        examples=[["Holocene"]],
    )

    earliestAgeOrLowestStage: Optional[List[str]] = Field(
        None,
        description="The full name of the earliest possible geochronologic age or lowest chronostratigraphic stage attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
        examples=[["Skullrockian"]],
    )

    # Geographic filters
    # gadmGid: Optional[List[str]] = Field(
    #     None,
    #     description="A GADM geographic identifier at any level, for example AGO, AGO.1_1, AGO.1.1_1 or AGO.1.1.1_1",
    #     examples=[["AGO.1_1"]],
    # )

    # gadmLevel0Gid: Optional[List[str]] = Field(
    #     None,
    #     description="A GADM geographic identifier at the zero level, for example AGO.",
    #     examples=[["AGO"]],
    # )

    # gadmLevel1Gid: Optional[List[str]] = Field(
    #     None,
    #     description="A GADM geographic identifier at the first level, for example AGO.1_1.",
    #     examples=[["AGO.1_1"]],
    # )

    # gadmLevel2Gid: Optional[List[str]] = Field(
    #     None,
    #     description="A GADM geographic identifier at the second level, for example AFG.1.1_1.",
    #     examples=[["AFG.1.1_1"]],
    # )

    # gadmLevel3Gid: Optional[List[str]] = Field(
    #     None,
    #     description="A GADM geographic identifier at the third level, for example AFG.1.1.1_1.",
    #     examples=[["AFG.1.1.1_1"]],
    # )

    waterBody: Optional[List[str]] = Field(
        None,
        description="The name of the water body in which the Location occurs.",
        examples=[["Atlantic Ocean"]],
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

    country: Optional[List[str]] = Field(
        None,
        description="The 2-letter country code (as per ISO-3166-1) of the country in which the occurrence was recorded.",
        examples=[["US"], ["GB", "FR", "DE"], ["AF", "ZA", "KE"]],
    )

    stateProvince: Optional[List[str]] = Field(
        None,
        description="The name of the next smaller administrative region than country (state, province, canton, department, region, etc.) in which the Location occurs. This term does not have any data quality checks; see also the GADM parameters. Parameter may be repeated.",
        examples=[["Leicestershire"]],
    )

    island: Optional[List[str]] = Field(
        None,
        description="The name of the island on or near which the location occurs.",
        examples=[["Zanzibar"]],
    )

    islandGroup: Optional[List[str]] = Field(
        None,
        description="The name of the island group in which the location occurs.",
        examples=[["Seychelles"]],
    )

    gbifRegion: Optional[List[GbifRegionEnum]] = Field(
        None,
        description="Gbif region based on country code. Parameter may be repeated.",
        examples=[
            [GbifRegionEnum.AFRICA],
            [GbifRegionEnum.NORTH_AMERICA, GbifRegionEnum.ANTARCTICA],
        ],
    )

    higherGeography: Optional[List[str]] = Field(
        None,
        description="Geographic name less specific than the information captured in the locality term. Parameter may be repeated.",
        examples=[["Argentina"]],
    )

    highestBiostratigraphicZone: Optional[List[str]] = Field(
        None,
        description="The full name of the highest possible geological biostratigraphic zone of the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
        examples=[["Blancan"]],
    )

    locality: Optional[List[str]] = Field(
        None,
        description="The specific description of the place. Use this when user insists on a locality name instead providing coordinates.",
        examples=[["Miami-Dade County, Florida"]],
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

    distanceFromCentroidInMeters: Optional[int] = Field(
        None,
        description="The horizontal distance (in metres) of the occurrence from the nearest centroid known to be used in automated georeferencing procedures, if that distance is 5000m or less. Occurrences (especially specimens) near a country centroid may have a poor-quality georeference, especially if coordinateUncertaintyInMeters is blank or large. Supports range queries.",
        examples=[[0, 500]],
    )

    geoDistance: Optional[str] = Field(
        None,
        description="Filters to match occurrence records with coordinate values within a specified distance of a coordinate. Distance may be specified in kilometres (km) or metres (m).",
        examples=["90,100,5km"],
    )

    geometry: Optional[List[str]] = Field(
        None,
        description="Searches for occurrences inside a polygon described in Well Known Text (WKT) format. Only POLYGON and MULTIPOLYGON are accepted WKT types. Polygons must have anticlockwise ordering of points. (A clockwise polygon represents the opposite area: the Earth's surface with a 'hole' in it. Such queries are not supported.)",
        examples=[["POLYGON ((30.1 10.1, 40 40, 20 40, 10 20, 30.1 10.1))"]],
    )

    elevation: Optional[int] = Field(
        None,
        description="Elevation (altitude) in metres above sea level. Parameter may be repeated or a range.",
        examples=[[1000, 1250]],
    )

    georeferencedBy: Optional[List[str]] = Field(
        None,
        description="Name of a person, group, or organization who determined the georeference (spatial representation) for the location.",
        examples=[["Brad Millen"]],
    )

    depth: Optional[int] = Field(
        None,
        description="Depth in metres relative to altitude. For example 10 metres below a lake surface with given altitude. Parameter may be repeated or a range.",
        examples=[[10, 20]],
    )

    # Temporal filters
    year: Optional[str] = Field(
        None,
        description="The 4 digit year. A year of 98 will be interpreted as AD 98. Supports range queries using comma-separated values. For instance: year='2020,2023' will return all records from 2020 and 2023 (not including 2021 and 2022). To express a range 'from YYY1 to YYY3' or 'YYY1, YYY2, YYY3', use the format 'YYY1,YYY3'. It does not support * wildcard.",
        examples=["2020", "2010,2020", "1998,2005"],
    )

    month: Optional[str] = Field(
        None,
        description="The month of the year, starting with 1 for January. Supports range queries. For instance: month='5,12' will return all records from May to December.",
        examples=["5", "1,12", "3,9"],
    )

    day: Optional[int] = Field(
        None,
        description="The day of the month, starting with 1 for the first day. Supports range queries. For instance: day='1,31' will return all records from the first to the 31st day of the month.",
        examples=["1", "1,31", "15"],
    )

    eventDate: Optional[List[str]] = Field(
        None,
        description="Occurrence date in ISO 8601 format: yyyy, yyyy-MM or yyyy-MM-dd.\n\n*Parameter may be repeated or a range.",
        examples=[["2020"], ["2020-01", "2020-12"], ["2000,2001-06-30"]],
    )

    eventId: Optional[List[str]] = Field(
        None,
        description="An identifier for the information associated with a sampling event. Parameter may be repeated.",
        examples=[["A 123"]],
    )

    # Taxonomic filters
    kingdomKey: Optional[List[int]] = Field(
        None,
        description="Kingdom classification key. Do not make up this parameter value. It must be explicitly mentioned in the user request.",
        examples=[[5], [1, 2, 3]],
    )

    phylumKey: Optional[List[int]] = Field(
        None,
        description="Phylum classification key. Do not make up this parameter value. It must be explicitly mentioned in the user request.",
        examples=[[44], [1, 2, 3]],
    )

    classKey: Optional[List[int]] = Field(
        None,
        description="Class classification key. Do not make up this parameter value. It must be explicitly mentioned in the user request.",
        examples=[[212], [1, 2, 3]],
    )

    orderKey: Optional[List[int]] = Field(
        None,
        description="Order classification key. Do not make up this parameter value. It must be explicitly mentioned in the user request.",
        examples=[[1448], [1, 2, 3]],
    )

    familyKey: Optional[List[int]] = Field(
        None,
        description="Family classification key. Do not make up this parameter value. It must be explicitly mentioned in the user request.",
        examples=[[2405], [1, 2, 3]],
    )

    genusKey: Optional[List[int]] = Field(
        None,
        description="Genus classification key. Do not make up this parameter value. It must be explicitly mentioned in the user request.",
        examples=[[2877951], [1, 2, 3]],
    )

    speciesKey: Optional[List[int]] = Field(
        None,
        description="Species classification key. Do not make up this parameter value. It must be explicitly mentioned in the user request.",
        examples=[[2476674], [1, 2, 3]],
    )

    taxonomicStatus: Optional[TaxonomicStatusEnum] = Field(
        None,
        description="Filters by the taxonomic status to distinguish between accepted names, synonyms, and doubtful names. Essential for taxonomic research and data quality control.",
        examples=[
            TaxonomicStatusEnum.ACCEPTED,
            TaxonomicStatusEnum.SYNONYM,
            TaxonomicStatusEnum.DOUBTFUL,
        ],
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

    identifiedBy: Optional[List[str]] = Field(
        None,
        description="The person who provided the taxonomic identification of the occurrence.",
        examples=[["Allison"]],
    )

    identifiedByID: Optional[List[str]] = Field(
        None,
        description="Identifier (e.g. ORCID) for the person who provided the taxonomic identification of the occurrence.",
        examples=[["https://orcid.org/0000-0001-6492-4016"]],
    )

    institutionCode: Optional[List[str]] = Field(
        None,
        description="An identifier of any form assigned by the source to identify the institution the record belongs to. Not guaranteed to be unique.",
        examples=[["K"], ["USNM", "BMNH"]],
    )

    datasetID: Optional[str] = Field(
        None,
        description="An identifier for the set of data. May be a global unique identifier or an identifier specific to a collection or institution.",
        examples=["https://doi.org/10.1594/PANGAEA.315492"],
    )

    datasetKey: Optional[List[UUID]] = Field(
        None,
        description="The occurrence dataset key (a UUID).",
        examples=[
            ["13b70480-bd69-11dd-b15f-b8a03c50a862"],
            ["e2e717bf-551a-4917-bdc9-4fa0f342c530"],
        ],
    )

    datasetName: Optional[str] = Field(
        None,
        description="The name identifying the data set from which the record was derived.",
        examples=["GBIF Backbone Taxonomy"],
    )

    collectionCode: Optional[List[str]] = Field(
        None,
        description="An identifier of any form assigned by the source to identify the physical collection or digital dataset uniquely within the context of an institution.",
        examples=[["F"], ["BIRD", "MAMMAL"]],
    )

    collectionKey: Optional[List[UUID]] = Field(
        None,
        description="A key (UUID) for a collection registered in the Global Registry of Scientific Collections.",
        examples=[["dceb8d52-094c-4c2c-8960-75e0097c6861"]],
    )

    recordNumber: Optional[List[str]] = Field(
        None,
        description="An identifier given to the record at the time it was recorded in the field; often links field notes to the event.",
        examples=[["1"], ["23", "234543"]],
    )

    recordedBy: Optional[List[str]] = Field(
        None,
        description="The person who recorded the occurrence.",
        examples=[["MiljoStyrelsen"], ["John Smith", "Jane Doe"]],
    )

    publishingCountry: Optional[List[str]] = Field(
        None,
        description="The 2-letter country code (as per ISO-3166-1) of the owning organization's country.",
        examples=[["AD"], ["US", "GB"]],
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

    lastInterpreted: Optional[List[str]] = Field(
        None,
        description="""This date the record was last modified in GBIF, in ISO 8601 format: yyyy, yyyy-MM, yyyy-MM-dd, or MM-dd.
        
        Note that this is the date the record was last changed in GBIF, not necessarily the date the record was first/last changed by the publisher. Data is re-interpreted when we change the taxonomic backbone, geographic data sources, or interpretation processes.
        
        Parameter may be repeated or a range.""",
        examples=[["2023-02"]],
    )

    # Other organism and specimen features
    sex: Optional[List[str]] = Field(
        None,
        description="The sex of the biological individual(s) represented in the occurrence.",
        examples=[["MALE"]],
    )

    lifeStage: Optional[List[str]] = Field(
        None,
        description="The age class or life stage of an organism at the time the occurrence was recorded, as defined in the GBIF LifeStage vocabulary](https://registry.gbif.org/vocabulary/LifeStage/concepts).",
        examples=[["JUVENILE"]],
    )

    preparations: Optional[List[str]] = Field(
        None,
        description="Preparation or preservation method for a specimen.",
        examples=[["pinned"]],
    )

    previousIdentifications: Optional[List[str]] = Field(
        None,
        description="Previous assignment of name to the organism.",
        examples=[["Chalepidae"]],
    )

    # material sample
    # associatedSequences: Optional[List[str]] = Field(
    #     None,
    #     description="Identifier (publication, global unique identifier, URI) of genetic sequence information associated with the material entity. Parameter may be repeated.",
    #     examples=[["http://www.ncbi.nlm.nih.gov/nuccore/U34853.1"]],
    # )

    # earliestEonOrLowestEonothem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the earliest possible geochronologic era or lowest chronostratigraphic erathem attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Mesozoic"]],
    # )

    # earliestEraOrLowestErathem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic eon or highest chrono-stratigraphic eonothem or the informal name ('Precambrian') attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Proterozoic"]],
    # )

    # earliestPeriodOrLowestSystem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the earliest possible geochronologic period or lowest chronostratigraphic system attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Neogene"]],
    # )

    # earliestPeriodOrLowestSystem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the earliest possible geochronologic period or lowest chronostratigraphic system attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Neogene"]],
    # )

    # earliestEpochOrLowestSeries: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the earliest possible geochronologic epoch or lowest chronostratigraphic series attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Holocene"]],
    # )

    # earliestEraOrLowestErathem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic eon or highest chrono-stratigraphic eonothem or the informal name ('Precambrian') attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Proterozoic"]],
    # )

    # earliestPeriodOrLowestSystem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the earliest possible geochronologic period or lowest chronostratigraphic system attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Neogene"]],
    # )

    # earliestEpochOrLowestSeries: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the earliest possible geochronologic epoch or lowest chronostratigraphic series attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Holocene"]],
    # )

    # earliestAgeOrLowestStage: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the earliest possible geochronologic age or lowest chronostratigraphic stage attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Skullrockian"]],
    # )

    # formation: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the lithostratigraphic formation from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Notch Peak Formation"]],
    # )

    # group: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the lithostratigraphic group from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Bathurst"]],
    # )

    # highestBiostratigraphicZone: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the highest possible geological biostratigraphic zone of the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Blancan"]],
    # )

    # latestEonOrHighestEonothem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic eon or highest chrono-stratigraphic eonothem or the informal name ('Precambrian') attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Proterozoic"]],
    # )

    # latestEraOrHighestErathem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic era or highest chronostratigraphic erathem attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Cenozoic"]],
    # )

    # latestPeriodOrHighestSystem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic period or highest chronostratigraphic system attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Neogene"]],
    # )

    # latestEonOrHighestEonothem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic eon or highest chrono-stratigraphic eonothem or the informal name ('Precambrian') attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Proterozoic"]],
    # )

    # latestEraOrHighestErathem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic era or highest chronostratigraphic erathem attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Cenozoic"]],
    # )

    # latestPeriodOrHighestSystem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic period or highest chronostratigraphic system attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Neogene"]],
    # )

    # latestEpochOrHighestSeries: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic epoch or highest chronostratigraphic series attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Pleistocene"]],
    # )

    # latestPeriodOrHighestSystem: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic period or highest chronostratigraphic system attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Neogene"]],
    # )

    # latestEpochOrHighestSeries: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic epoch or highest chronostratigraphic series attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Pleistocene"]],
    # )

    # latestAgeOrHighestStage: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic age or highest chronostratigraphic stage attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Boreal"]],
    # )

    # lowestBiostratigraphicZone: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the lowest possible geological biostratigraphic zone of the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Maastrichtian"]],
    # )

    # member: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the lithostratigraphic member from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Lava Dam Member"]],
    # )

    # latestAgeOrHighestStage: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the latest possible geochronologic age or highest chronostratigraphic stage attributable to the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Boreal"]],
    # )

    # lowestBiostratigraphicZone: Optional[List[str]] = Field(
    #     None,
    #     description="The full name of the lowest possible geological biostratigraphic zone of the stratigraphic horizon from which the material entity was collected. Parameter may be repeated.",
    #     examples=[["Maastrichtian"]],
    # )

    member: Optional[List[str]] = Field(
        None,
        description="The full name of the lithostratigraphic member from which the material entity was collected. Parameter may be repeated.",
        examples=[["Lava Dam Member"]],
    )

    associatedSequences: Optional[List[str]] = Field(
        None,
        description="A list (concatenated and separated) of identifiers (publication, global unique identifier, URI) of genetic sequence information associated with the material entity.",
        examples=[["http://www.ncbi.nlm.nih.gov/nuccore/U34853.1"]],
    )

    datasetId: Optional[List[str]] = Field(
        None,
        description="An identifier for the set of data. May be a global unique identifier or an identifier specific to a collection or institution. externalDocs: https://rs.tdwg.org/dwc/terms/datasetID",
        examples=[["https://doi.org/10.1594/PANGAEA.315492"]],
    )

    verbatimScientificName: Optional[List[str]] = Field(
        None,
        description="The scientific name provided to GBIF by the data publisher, before interpretation and processing by GBIF. Parameter may be repeated.",
        examples=[["Quercus robur L."]],
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


class GBIFOccurrenceSearchParams(GBIFOccurrenceBaseParams):
    """Parameters for GBIF occurrence search - matches API structure"""

    pass


class GBIFOccurrenceFacetsParams(GBIFOccurrenceBaseParams):
    """Parameters for GBIF occurrence faceting - extends search params with faceting options"""

    # Faceting parameters
    facet: Optional[List[str]] = Field(
        default=None,
        description="A facet name used to retrieve the most frequent values for a field. Facets are allowed for all search parameters except geometry and geoDistance. This parameter may be repeated to request multiple facets. Note terms not available for searching are not available for faceting. If omitted, only the total count is returned without breakdowns.",
        examples=[
            ["scientificName"],
            ["country", "year"],
            ["basisOfRecord", "kingdom"],
            ["datasetKey", "publishingCountry"],
        ],
    )

    facetLimit: Optional[int] = Field(
        100,
        ge=1,
        max=500,
        description="Used in combination with the facet parameter. Set facetLimit={#} to limit the number of facets returned.",
        examples=[10, 20, 50],
    )

    facetOffset: Optional[int] = Field(
        0,
        ge=0,
        description="Used in combination with the facet parameter. Set facetOffset={#} to offset the number of facets returned.",
        examples=[10, 30, 80],
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
        description="Simple full text search parameter covering scientific and vernacular names, species descriptions, distribution and entire classification. The value can be a simple word or phrase. Wildcards are not supported. Results are ordered by relevance. Only use this parameter if the user's request is vague and none of the other specific parameters are available.",
        examples=[
            "Puma concolor",
            "jaguar",
            "Quercus",
            "oak tree",
            "Panthera tigris",
            "endangered cats",
        ],
    )

    qField: Optional[QueryFieldEnum] = Field(
        description="Use it along with q parameter. Limits the q parameter to search in a specific field. Use it to narrow down the results. Use SCIENTIFIC_NAME when you know or have a good estimate of the scientific name of the species you are searching for. Use VERNACULAR_NAME when you want to find a species using its common name, which can vary by region or language. Use DESCRIPTION when you are looking for a species based on a keyword found in its general description rather than its name.",
        default=QueryFieldEnum.VERNACULAR_NAME,
        examples=[
            QueryFieldEnum.VERNACULAR_NAME,
            QueryFieldEnum.SCIENTIFIC_NAME,
            QueryFieldEnum.DESCRIPTION,
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

    page: Optional[int] = Field(
        None,
        ge=1,
        description="Page number for pagination. Use with limit for pagination. For example, limit=20 and page=3 returns the third page of 20 results.",
        examples=[1, 2, 3, 4, 5],
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
        description="Maximum number of facet values to return per facet field.",
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

    key: Optional[int] = Field(
        None,
        description="The GBIF key (taxon key) for the species. This is a required parameter that uniquely identifies the species in the GBIF backbone.",
        examples=[5231190, 2476674, 2877951],
    )

    name: Optional[str] = Field(
        None,
        description="The scientific name of the species. This is a required parameter that uniquely identifies the species in the GBIF backbone.",
        examples=["Panthera onca", "jaguar", "Quercus robur", "oak tree"],
    )

    rank: Optional[TaxonomicRankEnum] = Field(
        None,
        description="The taxonomic rank of the species. This is an optional parameter that can be used to filter the results by taxonomic rank.",
        examples=[
            TaxonomicRankEnum.SPECIES,
            TaxonomicRankEnum.GENUS,
            TaxonomicRankEnum.FAMILY,
            TaxonomicRankEnum.ORDER,
        ],
    )

    qField: Optional[QueryFieldEnum] = Field(
        None,
        description="The field to search in. This is an optional parameter that can be used to search in the scientificName or vernacularName field.",
        examples=[QueryFieldEnum.SCIENTIFIC_NAME, QueryFieldEnum.VERNACULAR_NAME],
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


class GBIFOccurrenceByIdParams(ProductionBaseModel):
    """Parameters for GBIF occurrence by ID - retrieves a single occurrence record by its GBIF ID"""

    gbifId: int = Field(
        ...,
        description="The GBIF ID (gbifId) for the occurrence. This is a required parameter that uniquely identifies the occurrence in the GBIF occurrence store.",
        examples=[1258202889, 5006758998, 4996399785],
    )


class GBIFDatasetSearchParams(ProductionBaseModel):
    """Parameters for GBIF dataset search - full-text search across all datasets with filtering options"""

    # Core search parameters
    q: Optional[str] = Field(
        None,
        description="Simple full text search parameter. The value for this parameter can be a simple word or a phrase. Wildcards are not supported. Only use this parameter if the user's request is vague and none of the other specific parameters are available.",
        examples=["bird observations", "plant specimens", "marine biodiversity"],
    )

    hl: Optional[bool] = Field(
        None,
        description="Set to true to highlight terms matching the query when in fulltext search fields. The highlight will be an emphasis tag of class `gbifHl`.",
        examples=[True, False],
    )

    # Dataset type filters
    type: Optional[DatasetTypeEnum] = Field(
        None,
        description="The primary type of the dataset.",
        examples=[
            DatasetTypeEnum.OCCURRENCE,
            DatasetTypeEnum.CHECKLIST,
            DatasetTypeEnum.METADATA,
            DatasetTypeEnum.SAMPLING_EVENT,
        ],
    )

    subtype: Optional[DatasetSubtypeEnum] = Field(
        None,
        description="The sub-type of the dataset.",
        examples=[
            DatasetSubtypeEnum.TAXONOMIC_AUTHORITY,
            DatasetSubtypeEnum.SPECIMEN,
            DatasetSubtypeEnum.OBSERVATION,
        ],
    )

    # Organization filters
    publishingOrg: Optional[str] = Field(
        None,
        description="Filters datasets by their publishing organization UUID key.",
        examples=["b542788f-0dc2-4a2b-b652-fceced449591"],
    )

    hostingOrg: Optional[str] = Field(
        None,
        description="Filters datasets by their hosting organization UUID key.",
        examples=["b542788f-0dc2-4a2b-b652-fceced449591"],
    )

    # Content filters
    keyword: Optional[str] = Field(
        None,
        description="Filters datasets by a case insensitive plain text keyword. The search is done on the merged collection of tags, the dataset keywordCollections and temporalCoverages.",
        examples=["biodiversity", "conservation", "taxonomy"],
    )

    decade: Optional[int] = Field(
        None,
        description="Filters datasets by their temporal coverage broken down to decades. Decades are given as a full year, e.g. 1880, 1960, 2000, etc.",
        examples=[1880, 1960, 2000, 2020],
    )

    publishingCountry: Optional[str] = Field(
        None,
        description="Filters datasets by their owning organization's country given as a ISO 639-1 (2 letter) country code.",
        examples=["US", "GB", "DE", "FR"],
    )

    hostingCountry: Optional[str] = Field(
        None,
        description="Filters datasets by their hosting organization's country given as a ISO 639-1 (2 letter) country code.",
        examples=["US", "GB", "DE", "FR"],
    )

    continent: Optional[ContinentEnum] = Field(
        None,
        description="Filters datasets by continent based on a 7 continent model.",
        examples=[
            ContinentEnum.NORTH_AMERICA,
            ContinentEnum.EUROPE,
            ContinentEnum.ASIA,
        ],
    )

    license: Optional[LicenseEnum] = Field(
        None,
        description="The dataset's licence.",
        examples=[
            LicenseEnum.CC0_1_0,
            LicenseEnum.CC_BY_4_0,
            LicenseEnum.CC_BY_NC_4_0,
        ],
    )

    # Additional filters
    projectId: Optional[str] = Field(
        None,
        description="Filter or facet based on the project ID of a given dataset. A dataset can have a project id if it is the result of a project.",
        examples=["AA003-AA003311F"],
    )

    taxonKey: Optional[int] = Field(
        None,
        description="A taxonKey is the primary id number used in GBIF to id a species (or some higher group). These are the id numbers found in the GBIF backbone taxonomy. Often you will see them in the URL of an occurrence search: https://www.gbif.org/occurrence/search?taxon_key=7412043. These are the most important keys and usually what other keys map back to (rule of thumb: “all keys lead to taxonKeys”).",
        examples=[5231190, 2476674, 2877951],
    )

    recordCount: Optional[str] = Field(
        None,
        description="Number of records of the dataset. Accepts ranges and a `*` can be used as a wildcard.",
        examples=["100,*", "1000,10000", "*"],
    )

    modifiedDate: Optional[str] = Field(
        None,
        description="Date when the dataset was modified the last time. Accepts ranges and a `*` can be used as a wildcard.",
        examples=["2022-05-01,*", "2020,2023", "*"],
    )

    doi: Optional[str] = Field(
        None,
        description="A DOI identifier.",
        examples=["10.15468/dl.abc123"],
    )

    networkKey: Optional[str] = Field(
        None,
        description="Network associated to a dataset.",
        examples=["b542788f-0dc2-4a2b-b652-fceced449591"],
    )

    endorsingNodeKey: Optional[str] = Field(
        None,
        description="Node key that endorsed this dataset's publisher.",
        examples=["b542788f-0dc2-4a2b-b652-fceced449591"],
    )

    installationKey: Optional[str] = Field(
        None,
        description="Key of the installation that hosts the dataset.",
        examples=["b542788f-0dc2-4a2b-b652-fceced449591"],
    )

    endpointType: Optional[EndpointTypeEnum] = Field(
        None,
        description="Type of the endpoint of the dataset.",
        examples=[
            EndpointTypeEnum.DWC_ARCHIVE,
            EndpointTypeEnum.EML,
            EndpointTypeEnum.BIOCASE,
        ],
    )

    category: Optional[str] = Field(
        None,
        description="Category of the dataset.",
        examples=["biodiversity", "taxonomy", "ecology"],
    )

    contactUserId: Optional[str] = Field(
        None,
        description="Filter datasets by contact user ID (e.g., ORCID).",
        examples=["0000-0001-2345-6789"],
    )

    contactEmail: Optional[str] = Field(
        None,
        description="Filter datasets by contact email address.",
        examples=["contact@example.org"],
    )

    # Faceting parameters
    facet: Optional[List[str]] = Field(
        None,
        description="A facet name used to retrieve the most frequent values for a field. This parameter may be repeated to request multiple facets.",
        examples=[
            ["type"],
            ["license", "publishingCountry"],
            ["type", "license", "publishingCountry"],
        ],
    )

    facetMinCount: Optional[int] = Field(
        None,
        ge=1,
        description="Used in combination with the facet parameter. Set to exclude facets with a count less than the specified value.",
        examples=[1, 10, 100],
    )

    facetMultiselect: Optional[bool] = Field(
        None,
        description="Used in combination with the facet parameter. Set to true to still return counts for values that are not currently filtered.",
        examples=[True, False],
    )

    facetLimit: Optional[int] = Field(
        None,
        ge=1,
        max=500,
        description="Facet parameters allow paging requests using the parameters facetOffset and facetLimit.",
        examples=[10, 50, 100],
    )

    facetOffset: Optional[int] = Field(
        None,
        ge=0,
        description="Facet parameters allow paging requests using the parameters facetOffset and facetLimit.",
        examples=[0, 50, 100],
    )

    # Pagination parameters
    limit: Optional[int] = Field(
        20,
        ge=1,
        le=100,
        description="Controls the number of results in the page. Using too high a value will be overwritten with the default maximum threshold.",
        examples=[10, 20, 50, 100],
    )

    offset: Optional[int] = Field(
        0,
        ge=0,
        description="Determines the offset for the search results. A limit of 20 and offset of 40 will get the third page of 20 results.",
        examples=[0, 20, 40],
    )
