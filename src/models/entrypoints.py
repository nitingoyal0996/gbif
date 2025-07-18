"""
Essential Pydantic models for GBIF API entrypoints.
"""

from enum import Enum
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field


class BasisOfRecord(str, Enum):
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


class Continent(str, Enum):
    AFRICA = "AFRICA"
    ANTARCTICA = "ANTARCTICA"
    ASIA = "ASIA"
    OCEANIA = "OCEANIA"
    EUROPE = "EUROPE"
    NORTH_AMERICA = "NORTH_AMERICA"
    SOUTH_AMERICA = "SOUTH_AMERICA"


class OccurrenceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"


class License(str, Enum):
    CC0_1_0 = "CC0_1_0"
    CC_BY_4_0 = "CC_BY_4_0"
    CC_BY_NC_4_0 = "CC_BY_NC_4_0"
    UNSPECIFIED = "UNSPECIFIED"
    UNSUPPORTED = "UNSUPPORTED"


class GBIFOccurrenceSearchParams(BaseModel):
    """Parameters for GBIF occurrence search - matches API structure with user-friendly interface."""
    
    # Core search parameters
    q: Optional[str] = Field(None, 
        description="Full-text search parameter (common name, scientific name, etc.)",
        examples=["Quercus robur", "oak", "human observation"]
    )
    
    scientificName: Optional[List[str]] = Field(None, 
        description="Scientific names from the GBIF backbone",
        examples=[["Quercus robur"], ["Homo sapiens", "Canis lupus"]]
    )
    
    occurrenceId: Optional[List[str]] = Field(None,
        description="Unique identifiers of occurrence records",
        examples=[["2005380410"], ["1234567890", "9876543210"]]
    )
    
    taxonKey: Optional[List[int]] = Field(None, 
        description="GBIF backbone taxon keys",
        examples=[[2877951], [2476674, 2877951]]
    )
    
    datasetKey: Optional[List[UUID]] = Field(None, 
        description="Occurrence dataset keys",
        examples=[["13b70480-bd69-11dd-b15f-b8a03c50a862"]]
    )
    
    basisOfRecord: Optional[List[BasisOfRecord]] = Field(None, 
        description="Basis of record types",
        examples=[[BasisOfRecord.PRESERVED_SPECIMEN], [BasisOfRecord.HUMAN_OBSERVATION, BasisOfRecord.OBSERVATION]]
    )
    
    catalogNumber: Optional[List[str]] = Field(None, 
        description="Identifiers within physical collections/datasets"
    )
    
    # Geographic filters
    country: Optional[List[str]] = Field(None, 
        description="ISO 3166-1 2-letter country codes",
        examples=[["US"], ["GB", "FR", "DE"]]
    )
    
    continent: Optional[List[Continent]] = Field(None, 
        description="Continents",
        examples=[[Continent.EUROPE], [Continent.NORTH_AMERICA, Continent.SOUTH_AMERICA]]
    )
    
    decimalLatitude: Optional[str] = Field(None, 
        description="Latitude in decimal degrees range",
        examples=["30,50", "-90,90"]
    )
    
    decimalLongitude: Optional[str] = Field(None, 
        description="Longitude in decimal degrees range",
        examples=["-180,180", "-100,-50"]
    )
    
    hasCoordinate: Optional[bool] = Field(None, 
        description="Whether the record has coordinates"
    )
    
    hasGeospatialIssue: Optional[bool] = Field(None, 
        description="Whether the record has spatial issues"
    )
    
    # Temporal filters
    year: Optional[str] = Field(None, 
        description="Year or year range",
        examples=["2020", "2010,2020", "2020,2021,2022"]
    )
    
    month: Optional[str] = Field(None, 
        description="Month or month range",
        examples=["5", "1,12", "3,6,9"]
    )
    
    eventDate: Optional[List[str]] = Field(None, 
        description="Date in ISO format: yyyy, yyyy-MM, yyyy-MM-dd",
        examples=[["2020"], ["2020-01", "2020-12"]]
    )
    
    # Taxonomic filters
    kingdomKey: Optional[List[int]] = Field(None, 
        description="Kingdom classification keys"
    )
    
    phylumKey: Optional[List[int]] = Field(None, 
        description="Phylum classification keys"
    )
    
    classKey: Optional[List[int]] = Field(None, 
        description="Class classification keys"
    )
    
    orderKey: Optional[List[int]] = Field(None, 
        description="Order classification keys"
    )
    
    familyKey: Optional[List[int]] = Field(None, 
        description="Family classification keys"
    )
    
    genusKey: Optional[List[int]] = Field(None, 
        description="Genus classification keys"
    )
    
    speciesKey: Optional[List[int]] = Field(None, 
        description="Species classification keys"
    )
    
    # Additional filters
    occurrenceStatus: Optional[OccurrenceStatus] = Field(None, 
        description="Presence/absence of occurrence"
    )
    
    license: Optional[List[License]] = Field(None, 
        description="License types",
        examples=[[License.CC0_1_0], [License.CC_BY_4_0, License.CC_BY_NC_4_0]]
    )
    
    institutionCode: Optional[List[str]] = Field(None, 
        description="Institution codes"
    )
    
    collectionCode: Optional[List[str]] = Field(None, 
        description="Collection codes"
    )
    
    recordedBy: Optional[List[str]] = Field(None, 
        description="Persons who recorded the occurrence"
    )
    
    identifiedBy: Optional[List[str]] = Field(None, 
        description="Persons who identified the occurrence"
    )
    
    typeStatus: Optional[List[str]] = Field(None, 
        description="Nomenclatural type status",
        examples=[["HOLOTYPE"], ["PARATYPE", "SYNTYPE"]]
    )
    
    isSequenced: Optional[bool] = Field(None, 
        description="Whether occurrence has associated sequences"
    )
    
    mediaType: Optional[List[str]] = Field(None, 
        description="Types of associated media",
        examples=[["StillImage"], ["MovingImage", "Sound"]]
    )
    
    # Pagination parameters
    limit: Optional[int] = Field(
        100,
        ge=0,
        le=300,
        description="Number of results per page (max 300). A limit of 0 will return no record data."
    )
    
    offset: Optional[int] = Field(
        0,
        ge=0, 
        description="Offset for pagination"
    )


class GBIFOccurrenceFacetsParams(BaseModel):
    """Parameters for GBIF occurrence faceting - extends search params with faceting options."""
    
    # Inherit all search parameters
    q: Optional[str] = Field(None, description="Full-text search parameter")
    scientificName: Optional[List[str]] = Field(None, description="Scientific names from the GBIF backbone")
    occurrenceId: Optional[List[str]] = Field(None, description="Unique identifiers of occurrence records")
    taxonKey: Optional[List[int]] = Field(None, description="GBIF backbone taxon keys")
    datasetKey: Optional[List[UUID]] = Field(None, description="Occurrence dataset keys")
    basisOfRecord: Optional[List[BasisOfRecord]] = Field(None, description="Basis of record types")
    catalogNumber: Optional[List[str]] = Field(None, description="Identifiers within physical collections/datasets")
    
    # Geographic filters
    country: Optional[List[str]] = Field(None, description="ISO 3166-1 2-letter country codes")
    continent: Optional[List[Continent]] = Field(None, description="Continents")
    decimalLatitude: Optional[str] = Field(None, description="Latitude in decimal degrees range")
    decimalLongitude: Optional[str] = Field(None, description="Longitude in decimal degrees range")
    hasCoordinate: Optional[bool] = Field(None, description="Whether the record has coordinates")
    hasGeospatialIssue: Optional[bool] = Field(None, description="Whether the record has spatial issues")
    
    # Temporal filters
    year: Optional[str] = Field(None, description="Year or year range")
    month: Optional[str] = Field(None, description="Month or month range")
    eventDate: Optional[List[str]] = Field(None, description="Date in ISO format")
    
    # Taxonomic filters
    kingdomKey: Optional[List[int]] = Field(None, description="Kingdom classification keys")
    phylumKey: Optional[List[int]] = Field(None, description="Phylum classification keys")
    classKey: Optional[List[int]] = Field(None, description="Class classification keys")
    orderKey: Optional[List[int]] = Field(None, description="Order classification keys")
    familyKey: Optional[List[int]] = Field(None, description="Family classification keys")
    genusKey: Optional[List[int]] = Field(None, description="Genus classification keys")
    speciesKey: Optional[List[int]] = Field(None, description="Species classification keys")
    
    # Additional filters
    occurrenceStatus: Optional[OccurrenceStatus] = Field(None, description="Presence/absence of occurrence")
    license: Optional[List[License]] = Field(None, description="License types")
    institutionCode: Optional[List[str]] = Field(None, description="Institution codes")
    collectionCode: Optional[List[str]] = Field(None, description="Collection codes")
    recordedBy: Optional[List[str]] = Field(None, description="Persons who recorded the occurrence")
    identifiedBy: Optional[List[str]] = Field(None, description="Persons who identified the occurrence")
    typeStatus: Optional[List[str]] = Field(None, description="Nomenclatural type status")
    isSequenced: Optional[bool] = Field(None, description="Whether occurrence has associated sequences")
    mediaType: Optional[List[str]] = Field(None, description="Types of associated media")
    
    # Faceting parameters
    facet: List[str] = Field(
        ...,
        description="Fields to facet by",
        examples=[["scientificName"], ["country", "year"], ["basisOfRecord", "kingdom"]]
    )
    
    facetMincount: Optional[int] = Field(
        1,
        description="Minimum count for facet values",
        ge=1
    )
    
    facetMultiselect: Optional[bool] = Field(
        False,
        description="Allow multi-select faceting"
    )
    
    # Pagination parameters
    limit: Optional[int] = Field(
        0,
        ge=0,
        le=300,
        description="Number of results per page (0 for facets only)"
    )
    
    offset: Optional[int] = Field(
        0,
        ge=0, 
        description="Offset for pagination"
    )
