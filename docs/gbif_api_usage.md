# GBIF Agent

## Usage Categories

### 1. Occurrence Data Retrieval

#### Use Case 1.1: Individual Occurrence Record Retrieval  
  \
**Purpose**: Retrieve detailed information about specific biodiversity observations or specimens from GBIF.

Agent uses the `GET /v1/occurrence/{gbifId}` endpoint. This follows a direct ID-based lookup pattern where the response provides a single occurrence record with complete metadata.

**Example Query:** "Find occurrence record 5292056925"

#### Use Case 1.2: Occurrence Record Search

Discover occurrence records based on taxonomic, geographic, temporal, and methodological criteria.

The occurrence search functionality utilizes the `GET /v1/occurrence/search` endpoint. This endpoint supports multi-parameter filtering with paginated results with offset parameters.

The system supports comprehensive filtering across multiple categories. Taxonomic filters include scientificName, taxonKey, and hierarchical taxonomic keys such as kingdomKey, phylumKey, classKey, orderKey, familyKey, genusKey, and speciesKey. Geographic filtering encompasses country, continent, stateProvince, decimalLatitude, decimalLongitude, and complex geometry parameters. Temporal filtering supports year, month, eventDate, and dateRange specifications. Data quality filters include basisOfRecord, occurrenceStatus, hasCoordinate, and hasGeospatialIssue parameters. Institutional filtering covers institutionCode, collectionCode, datasetKey, and publishingOrg. Collection-specific filters include recordedBy, identifiedBy, catalogNumber, and recordNumber parameters.

**Example Query:** "Find records of birds in Gainesville, Florida, United States from 2014-2016"

#### Use Case 1.3: Occurrence Record Faceted Search
  \
**Purpose:** Search and breakdowns of occurrence data

Aggregation uses the same `GET /v1/occurrence/search` endpoint but with GBIF faceting parameters. The request pattern mirrors standard search functionality but automatically sets `limit=0` and includes facet parameters to generate aggregated counts grouped by specified dimensions. The faceting system supports any valid occurrence parameter as a grouping dimension supported by the GBIF API for faceting operations.

**Example Query:** "How many species occurrences does GBIF have for Temperate Asia?"

### 2. Species and Taxonomic Information Services

#### Use Case 2.1: Scientific Name Resolution and Matching

  \
**Purpose:** Convert scientific names to standardized GBIF identifiers

Scientific name resolution utilizes the `GET /v2/species/match` endpoint. If there is a scientific name strings in input and it returns matched taxa with usage keys and taxonomic hierarchy information. The agent entrypoint automatically invokes this service internally whenever scientificName parameters are provided in user queries. It is similar to using `rgbif` package search

The resolution process follows a systematic approach beginning with the extraction of scientific names from user queries using LLM parsing. The system then calls the species match API for each identified name and validates that the returned taxonomic rank matches the expected taxonomic level. Successfully resolved names result in the replacement of scientificName parameters with their corresponding taxonKeys for improved search performance. Throughout this process, the system generates detailed artifacts for tracking resolution results and maintaining data provenance.

**Example Query:** N/A. Agent usage it internally

#### Use Case 2.2: Species Search

  \
**Purpose:** Find species and taxonomic entities using flexible search criteria.

Species discovery employs the `GET /v1/species/search` endpoint. This supports species search queries with filtering capabilities, returning paginated species results. 

The search system provides flexible query capabilities supporting both scientific names and vernacular names as query fields. Filtering options also include taxonomic rank, conservation status, habitat preferences, threat levels, and dataset-specific searches.

**Example Query:** "Search for species named Quercus"

#### Use Case 2.3: Species Faceted Search

  \
**Purpose:** search and breakdown species data

This utilizes the same `GET /v1/species/search` endpoint with GBIF faceting parameters. It applies standard search parameters while automatically setting `limit=0` and enabling faceting functionality to generate aggregated results rather than individual species records.


**Example Query:** "How many species are in the family Rosaceae?"

#### Use Case 2.4: Species Taxonomic Information Retrieval

  \
**Purpose:** Gather complete taxonomic context including hierarchy, relationships, and synonymy.

Comprehensive taxonomic information retrieval employs a sophisticated multi-endpoint approach utilizing parallel API calls to gather complete taxonomic context. It queries multiple endpoints including the primary species endpoint `GET /v1/species/{key}`, taxonomic hierarchy through `GET /v1/species/{key}/parents`, child taxa via `GET /v1/species/{key}/children`, synonymous names through `GET /v1/species/{key}/synonyms`, and detailed name information using `GET /v1/species/{key}/name`. The agent determine the API calls based on user query intent.

**Example Query:** "Get taxonomic information for Rattus including synonyms and children"

### 3. Dataset Search

#### Use Case 3.1: Dataset Search

  \
**Purpose:** Find and analyze data sources and collections within the GBIF network.

Dataset search utilizes the `GET /v1/dataset/search` endpoint. The filters are parsed through the user request and locate relevant datasets, returning dataset information.

The search system provides extensive filtering capabilities across multiple dimensions. Metadata filtering encompasses title, description, and keyword searches for content-based discovery. Geographic filtering includes publishing country specifications and geographic coverage parameters. Technical filtering supports dataset type, licensing information, and format specifications. Taxonomic filtering enables discovery based on taxonomic coverage using taxonKey parameters. Organizational filtering covers publishing organizations, network affiliations, and installation-specific searches.

**Example Query:** "Find datasets about marine biodiversity from Nordic countries"

## Portal integration - URL Translation

- For each usage; agent generates the API request url as well as portal integration url which maintains continuity by providing direct links to corresponding dataset portal pages for detailed exploration to the users.

API URLs are automatically converted to corresponding portal URLs:

```python
# API URL
https://api.gbif.org/v1/occurrence/search?taxonKey=212&country=US

# Portal URL  
https://gbif.org/occurrence/search?taxonKey=212&country=US
```
---

## Parameter Processing

### Enums
The agent automatically converts enumerated values to their string representations using pydantic models. Enums for variables are the same as described in the GBIF OpenAPI Specifications.

```python
# Enum values extracted using .value attribute
BasisOfRecord.PRESERVED_SPECIMEN → "PRESERVED_SPECIMEN"
```

### Parameter List
Multiple values for the same parameter are handled using URL encoding.

```python
taxonKey=2435098&taxonKey=2435099&taxonKey=2435100
```

### Status Codes
All API requests include error handling to reflect the correct error to the iChatBio UI:
- HTTP status code validation
- Error logging with request context
- User-friendly error messages
- Artifact creation even for failed requests (for tracking)


#### Automatic Parameter Resolution
When users provide taxonomic names without specific keys, the system:
1. Extracts taxonomic names using LLM analysis
2. Resolves names to GBIF keys via species match API
3. Maps resolved keys to appropriate parameter fields
4. Updates request parameters before API calls


## Example Usage: Find occurrence records

![GBIF Agent Architecture](diagram.png)

The diagram above illustrates the high-level flow of how the GBIF agent creates a query to search occurrence records from the user request