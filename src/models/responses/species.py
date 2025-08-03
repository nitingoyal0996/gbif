"""
Pydantic models for GBIF Species API responses based on the OpenAPI specification.
"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class NameUsage(BaseModel):
    """Name usage response from GBIF Species API."""
    
    # Required fields
    key: int = Field(..., description="The name usage key that uniquely identifies this name usage.")
    datasetKey: str = Field(..., description="The checklist that hosts this name usage.")
    issues: List[str] = Field(..., description="Data quality issues found during processing.")
    origin: str = Field(..., description="The origin of this name usage.")
    scientificName: str = Field(..., description="The scientific name, with date and authorship information if available.")
    
    # Optional fields
    nubKey: Optional[int] = Field(None, description="The taxon key of the matching backbone name usage.")
    nameKey: Optional[int] = Field(None, description="The key for retrieving a parsed name object.")
    taxonID: Optional[str] = Field(None, description="The original taxonID of the name usage as found in the source.")
    sourceTaxonKey: Optional[int] = Field(None, description="The key of the name usage from which this backbone taxon derives.")
    
    # Taxonomic classification
    kingdom: Optional[str] = Field(None, description="Kingdom.")
    phylum: Optional[str] = Field(None, description="Phylum.")
    class_: Optional[str] = Field(None, alias="class", description="Class.")
    order: Optional[str] = Field(None, description="Order.")
    family: Optional[str] = Field(None, description="Family.")
    genus: Optional[str] = Field(None, description="Genus.")
    subgenus: Optional[str] = Field(None, description="Subgenus.")
    species: Optional[str] = Field(None, description="Species.")
    
    # Taxonomic keys
    kingdomKey: Optional[int] = Field(None, description="Name usage key of the kingdom.")
    phylumKey: Optional[int] = Field(None, description="Name usage key of the phylum.")
    classKey: Optional[int] = Field(None, description="Name usage key of the class.")
    orderKey: Optional[int] = Field(None, description="Name usage key of the order.")
    familyKey: Optional[int] = Field(None, description="Name usage key of the family.")
    genusKey: Optional[int] = Field(None, description="Name usage key of the genus.")
    subgenusKey: Optional[int] = Field(None, description="Name usage key of the subgenus.")
    speciesKey: Optional[int] = Field(None, description="Name usage key of the species.")
    
    # Additional fields
    constituentKey: Optional[str] = Field(None, description="The optional sub-dataset key for this usage.")
    parentKey: Optional[int] = Field(None, description="The name usage key of the immediate parent.")
    parent: Optional[str] = Field(None, description="The scientific name of the parent.")
    proParteKey: Optional[int] = Field(None, description="The primary name usage key for a pro parte synonym.")
    acceptedKey: Optional[int] = Field(None, description="The name usage key of the accepted name.")
    accepted: Optional[str] = Field(None, description="The scientific name of the accepted name.")
    basionymKey: Optional[int] = Field(None, description="The name usage key of the basionym.")
    basionym: Optional[str] = Field(None, description="The scientific name of the basionym.")
    canonicalName: Optional[str] = Field(None, description="The canonical name; the name without authorship or references.")
    vernacularName: Optional[str] = Field(None, description="A common or vernacular name for this usage.")
    authorship: Optional[str] = Field(None, description="The authorship for the scientific name.")
    nameType: Optional[str] = Field(None, description="The type of name string classified by Checklistbank.")
    rank: Optional[str] = Field(None, description="The rank for this usage.")
    taxonomicStatus: Optional[str] = Field(None, description="The taxonomic status of this name usage.")
    nomenclaturalStatus: Optional[List[str]] = Field(None, description="The nomenclatural status of this name usage.")
    isExtinct: Optional[bool] = Field(None, description="Whether this taxon is extinct.")
    numDescendants: Optional[int] = Field(None, description="The number of descendant taxa.")
    numOccurrences: Optional[int] = Field(None, description="The number of occurrence records for this taxon.")
    habitat: Optional[str] = Field(None, description="The habitat of this taxon.")
    threatStatus: Optional[str] = Field(None, description="The IUCN threat status of this taxon.")
    description: Optional[str] = Field(None, description="A description of this taxon.")
    accordingTo: Optional[str] = Field(None, description="The source of this information.")
    source: Optional[str] = Field(None, description="The source of this name usage.")
    sourceId: Optional[str] = Field(None, description="The source ID of this name usage.")
    sourceUrl: Optional[str] = Field(None, description="The source URL of this name usage.")
    sourceVersion: Optional[str] = Field(None, description="The source version of this name usage.")
    sourceTitle: Optional[str] = Field(None, description="The source title of this name usage.")
    sourceDescription: Optional[str] = Field(None, description="The source description of this name usage.")
    sourceContact: Optional[str] = Field(None, description="The source contact of this name usage.")
    sourceLogoUrl: Optional[str] = Field(None, description="The source logo URL of this name usage.")
    sourceHomepage: Optional[str] = Field(None, description="The source homepage of this name usage.")
    sourceRights: Optional[str] = Field(None, description="The source rights of this name usage.")
    sourceCitation: Optional[str] = Field(None, description="The source citation of this name usage.")
    sourceDoi: Optional[str] = Field(None, description="The source DOI of this name usage.")
    sourceIdentifier: Optional[str] = Field(None, description="The source identifier of this name usage.")
    sourceModified: Optional[str] = Field(None, description="The source modified date of this name usage.")
    sourceAccessed: Optional[str] = Field(None, description="The source accessed date of this name usage.")
    sourceCreated: Optional[str] = Field(None, description="The source created date of this name usage.")
    sourceUpdated: Optional[str] = Field(None, description="The source updated date of this name usage.")
    sourcePublished: Optional[str] = Field(None, description="The source published date of this name usage.")
    sourceLanguage: Optional[str] = Field(None, description="The source language of this name usage.")
    sourceLicense: Optional[str] = Field(None, description="The source license of this name usage.")
    sourceRightsHolder: Optional[str] = Field(None, description="The source rights holder of this name usage.")
    sourceDatasetKey: Optional[str] = Field(None, description="The source dataset key of this name usage.")
    sourceConstituentKey: Optional[str] = Field(None, description="The source constituent key of this name usage.")
    sourceParentKey: Optional[int] = Field(None, description="The source parent key of this name usage.")
    sourceProParteKey: Optional[int] = Field(None, description="The source pro parte key of this name usage.")
    sourceAcceptedKey: Optional[int] = Field(None, description="The source accepted key of this name usage.")
    sourceBasionymKey: Optional[int] = Field(None, description="The source basionym key of this name usage.")
    sourceScientificName: Optional[str] = Field(None, description="The source scientific name of this name usage.")
    sourceCanonicalName: Optional[str] = Field(None, description="The source canonical name of this name usage.")
    sourceVernacularName: Optional[str] = Field(None, description="The source vernacular name of this name usage.")
    sourceAuthorship: Optional[str] = Field(None, description="The source authorship of this name usage.")
    sourceNameType: Optional[str] = Field(None, description="The source name type of this name usage.")
    sourceRank: Optional[str] = Field(None, description="The source rank of this name usage.")
    sourceTaxonomicStatus: Optional[str] = Field(None, description="The source taxonomic status of this name usage.")
    sourceNomenclaturalStatus: Optional[str] = Field(None, description="The source nomenclatural status of this name usage.")
    sourceIsExtinct: Optional[bool] = Field(None, description="The source is extinct flag of this name usage.")
    sourceNumDescendants: Optional[int] = Field(None, description="The source number of descendants of this name usage.")
    sourceNumOccurrences: Optional[int] = Field(None, description="The source number of occurrences of this name usage.")
    sourceHabitat: Optional[str] = Field(None, description="The source habitat of this name usage.")
    sourceThreatStatus: Optional[str] = Field(None, description="The source threat status of this name usage.")
    sourceDescription: Optional[str] = Field(None, description="The source description of this name usage.")
    sourceAccordingTo: Optional[str] = Field(None, description="The source according to of this name usage.")


class PagingResponseNameUsage(BaseModel):
    """Paged response containing NameUsage objects."""
    
    offset: int = Field(..., description="The offset of the results within all the search results.")
    limit: int = Field(..., description="The limit used. Note the limit returned may be lower than the limit requested.")
    endOfRecords: bool = Field(..., description="True if this page of search results is the final page.")
    count: Optional[int] = Field(None, description="The total number of records returned by the search.")
    results: List[NameUsage] = Field(..., description="Search results.")


SpeciesAPIResponse = Union[NameUsage, PagingResponseNameUsage] 