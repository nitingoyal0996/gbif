# GBIF Agent Entrypoints Overview

## Occurrences Entrypoints

### 1. `count_occurrence_records`
- **Functionality:** Provides statistical summaries, counts, and breakdowns of occurrence data using facets (aggregation, not individual records).
- **Parameter Model:** [`GBIFOccurrenceFacetsParams`](src/models/entrypoints.py) - extends occurrence search params with required `facet` parameter
- **Request Inference:** Triggered by "how many", "count of", "breakdown by", or "summary of" requests. Validated using [`OccurrenceFacetsParamsValidator`](src/models/validators.py).
- **API Request Construction:**
  - **Scientific Name Resolution:** If `scientificName` provided, calls `https://api.gbif.org/v2/species/match?scientificName=<name>` to get taxonKey
  - **Main API Call:** `https://api.gbif.org/v1/occurrence/search?facet=<fields>&limit=0&<filters>`
  - **Portal URL:** `https://gbif.org/occurrence/search?<same-params>`
- **Response Handling:** 
  - Extracts pagination info (count, limit, offset) and logs it
  - Creates artifact with JSON data and portal_url metadata
  - Generates response summary using `_generate_response_summary()` function
  - Handles error cases with detailed logging and user-friendly error messages
- **Technical Documentation:** [GBIF Occurrence Search API](https://techdocs.gbif.org/en/openapi/v1/occurrence/#/Searching%20occurrences/searchOccurrences)
- **Source:** [`count_occurrence_records.py`](src/entrypoints/occurrences/count_occurrence_records.py)
- **Examples:**
```yaml
Request: How many species occurrences does GBIF have for Temperate Asia?

Parameters:
{
    "gbifRegion": [
        "ASIA"
    ],
    "limit": 0,
    "facet": [
        "speciesKey"
    ]
}

Response:
"According to GBIF, there are 173,629,585 species occurrence records for Temperate Asia. If you would like to explore these records further, you can view them in the GBIF portal here. Let me know if you’d like a breakdown by species or additional details from these results."
```

---

### 2. `find_occurrence_by_id`
- **Functionality:** Retrieves a single occurrence record by its unique GBIF identifier.
- **Parameter Model:** [`GBIFOccurrenceByIdParams`](src/models/entrypoints.py) - simple model with only `gbifId: int` field
- **Request Inference:** Triggered by "get details for ID", "look up occurrence", or "find record" with specific GBIF ID. Validated using [`OccurrenceSearchByIdParamsValidator`](src/models/validators.py).
- **API Request Construction:**
  - **Main API Call:** `https://api.gbif.org/v1/occurrence/{gbifId}` (no query parameters)
  - **Portal URL:** `https://gbif.org/occurrence/{gbifId}`
- **Response Handling:** Extracts single record, logs key fields (scientificName, basisOfRecord, etc.), creates artifact, handles 404 errors for invalid IDs
- **Technical Documentation:** [GBIF Occurrence Details API](https://techdocs.gbif.org/en/openapi/v1/occurrence/#/Retrieving%20occurrence%20records/getOccurrence)
- **Source:** [`find_occurrence_by_id.py`](src/entrypoints/occurrences/find_occurrence_by_id.py)

Example:
```yaml
Message: find the occurrence record 5292056925

Parameters: { "gbifId": 5292056925 }

Response: According to GBIF, the occurrence record with ID 5292056925 refers to Rattus rattus (Linnaeus, 1758) observed in Florida, USA, in 2016 by Aaron Stoll. You can view the full record in the GBIF portal here.

```

---

### 3. `find_occurrence_records`
- **Functionality:** Searches for and retrieves a list of occurrence records matching specific filters (primary tool for fetching raw data).
- **Parameter Model:** [`GBIFOccurrenceSearchParams`](src/models/entrypoints.py) - comprehensive model with 50+ filter parameters including geographic, temporal, taxonomic filters
- **Request Inference:** Triggered by "find", "list", or "show records of" with filters. Does NOT perform summaries/counts. Validated using [`OccurrenceSearchParamsValidator`](src/models/validators.py).
- **API Request Construction:**
  - **Scientific Name Resolution:** If `scientificName` provided, calls `https://api.gbif.org/v2/species/match?scientificName=<name>` to get taxonKey
  - **Main API Call:** `https://api.gbif.org/v1/occurrence/search?<filters>&limit=100&offset=0`
  - **Portal URL:** `https://gbif.org/occurrence/search?<same-params>`
- **Response Handling:** 
  - Extracts pagination info (count, limit, offset) and logs it
  - Creates artifact with JSON data and portal_url metadata  
  - Generates response summary using `_generate_response_summary()` function
  - Handles error cases with detailed logging and user-friendly error messages
- **Technical Documentation:** [GBIF Occurrence Search API](https://techdocs.gbif.org/en/openapi/v1/occurrence/#/Searching%20occurrences/searchOccurrences)
- **Source:** [`find_occurrence_records.py`](src/entrypoints/occurrences/find_occurrence_records.py)

```yaml
Req: find records of birds (Aves) in florida united state from 2014-2016

Parameter:
{
    "scientificName": [
        "Aves"
    ],
    "country": [
        "US"
    ],
    "stateProvince": [
        "Florida"
    ],
    "year": "2014,2016"
}

Response:
"There are 7,810,880 occurrence records of birds (Aves) in Florida, United States, from 2014 to 2016 according to GBIF. You can view these records in detail on the GBIF portal at this link: https://gbif.org/occurrence/search?taxonKey=212&country=US&stateProvince=Florida&year=2014%2C2016.

If you need to see sample records or specific details, please let me know!"

--------------------------------------------
Message: I am looking for person who collected honey bee and bumblebees in North America on 15 Aug 2015, only human observations or museum specimens

Parameters: {
    "scientificName": [
        "Apis",
        "Bombus"
    ],
    "basisOfRecord": [
        "HUMAN_OBSERVATION",
        "PRESERVED_SPECIMEN"
    ],
    "continent": [
        "NORTH_AMERICA"
    ],
    "eventDate": [
        "2015-08-15"
    ]
}

Response: According to GBIF, collectors who recorded honey bees (Apis) and bumblebees (Bombus) in North America on August 15, 2015 (using human observations or preserved specimens) include: Carolyn Gritzmaker, Jesse Rorabaugh, Roy Pilcher, Gilberto Ponce Tejeda, Andy, Ernesto, krancmm, Clayton D'Orsay, Daniel Atha, Jerry Cannon, Don Sutherland, molanic, Rick Ballard, Joe Kunkel, and Bill Crins (GBIF Occurrence).

Would you like to see more details about their records or information about specific individuals? You can also view the full set of records in the GBIF portal here.

--------------------------------------------
Req: I am looking for person who collected honey bee and bumblebees in North America on 15 Aug 2015, only human observations or museum specimens

Parameters:
{
    "scientificName": [
        "Apis",
        "Bombus"
    ],
    "basisOfRecord": [
        "HUMAN_OBSERVATION",
        "PRESERVED_SPECIMEN"
    ],
    "continent": [
        "NORTH_AMERICA"
    ],
    "eventDate": [
        "2015-08-15"
    ]

}

Response:
"According to GBIF, here are some people who collected honey bee and bumblebee records in North America on August 15, 2015, based on human observations or museum specimens:

Andy (Bombus pensylvanicus, Texas, USA, iNaturalist research-grade observations)
Bill Crins (Bombus griseocollis, Ontario, Canada, iNaturalist research-grade observations)
Carolyn Gritzmaker (Apis mellifera, Texas, USA, iNaturalist research-grade observations)
Clayton D'Orsay (Bombus ternarius, Nova Scotia, Canada, iNaturalist research-grade observations)
Daniel Atha (Apis mellifera, New York, USA, iNaturalist research-grade observations)
There are more unique collectors in the dataset. If you would like to see the complete list or additional details, please let me know. The results can also be viewed in the GBIF portal at this link."
```
---

## Registry/Dataset Entrypoint

### 4. `find_datasets`
- **Functionality:** Finds datasets, collections, or data sources in the GBIF Registry based on metadata (NOT individual data points inside datasets).
- **Parameter Model:** [`GBIFDatasetSearchParams`](src/models/entrypoints.py) - includes filters like type, keyword, publishingCountry, license, taxonKey, faceting support
- **Request Inference:** Triggered by "find datasets", "search for collections", "list data sources about" topic. Validated using [`DatasetSearchParamsValidator`](src/models/validators.py).
- **API Request Construction:**
  - **Main API Call:** `https://api.gbif.org/v1/dataset/search?<filters>&limit=20&offset=0`
  - **Portal URL:** `https://gbif.org/dataset/search?<same-params>`
- **Response Handling:** Extracts dataset results, logs total count, creates artifact with metadata information
- **Technical Documentation:** [GBIF Dataset Search API](https://techdocs.gbif.org/en/openapi/v1/registry/#/Datasets/searchDatasets)
- **Source:** [`find_datasets.py`](src/entrypoints/registry/find_datasets.py)

Example:
```yaml
Message: 
Parameter:
Response:
```
---

## Species Entrypoints

### 5. `count_species_records`
- **Functionality:** Provides statistical counts and summaries of species/taxonomic entities (NOT their real-world observations).
- **Parameter Model:** [`GBIFSpeciesFacetsParams`](src/models/entrypoints.py) - extends species search params with optional facet parameters
- **Request Inference:** Triggered by "how many species", "count of species", "breakdown of species by" taxonomic groups. Validated using [`SpeciesFacetsParamsValidator`](src/models/validators.py).
- **API Request Construction:**
  - **Main API Call:** `https://api.gbif.org/v1/species/search?{filters}&facet=<fields>&limit=0&<filters>`
  - **Portal URL:** `https://gbif.org/species/search?{filters}`
- **Response Handling:** Extracts faceted species counts, logs pagination info, creates artifact with statistical results
- **Technical Documentation:** [GBIF Species Search API](https://techdocs.gbif.org/en/openapi/v1/species/#/Searching%20name%20usages/searchNameUsages)
- **Source:** [`count_species_records.py`](src/entrypoints/species/count_species_records.py)

Example:
```yaml
Message: 
Parameter:
Response:
```
---

### 6. `find_species_records`
- **Functionality:** Finds species using general search term (scientific/common name) with optional filters. Returns potential matches with usageKey (taxonKey). For GBIF Backbone Taxonomy, uses datasetKey `d7dddbf4-2cf0-4f39-9b2a-bb099caae36c`.
- **Parameter Model:** [`GBIFSpeciesSearchParams`](src/models/entrypoints.py) - includes `q` (query), `qField` (SCIENTIFIC_NAME/VERNACULAR_NAME), filters like rank, status, habitat, threat
- **Request Inference:** Triggered by "search for a species", "look up" organism. Does NOT retrieve detailed hierarchies or count occurrences. Validated using [`SpeciesSearchParamsValidator`](src/models/validators.py).
- **API Request Construction:**
  - **Main API Call:** `https://api.gbif.org/v1/species/search?q=<term>&qField=<field>&<filters>&limit=20`
  - **Portal URL:** `https://gbif.org/species/search?<same-params>`
- **Response Handling:** Extracts species matches, logs pagination info, creates artifact with species list
- **Technical Documentation:** [GBIF Species Search API](https://techdocs.gbif.org/en/openapi/v1/species/#/Searching%20name%20usages/searchNameUsages)
- **Source:** [`find_species_records.py`](src/entrypoints/species/find_species_records.py)

Example:
```yaml
Message: 
Parameter:
Response:
```
---

### 7. `find_taxonomic_information`
- **Functionality:** Retrieves comprehensive taxonomic information (hierarchy, children, synonyms) for a species by taxonKey or name. **UNIQUE FLOW:** Makes multiple parallel API calls and uses AI for best match selection.
- **Parameter Model:** [`GBIFSpeciesTaxonomicParams`](src/models/entrypoints.py) - includes `key`, `name`, `rank`, `qField`, boolean flags for includeParents/Children/Synonyms
- **Request Inference:** Triggered by "find taxonomic information of", "synonyms of", "children of", "parents of" species. Validated using [`SpeciesTaxonomicParamsValidator`](src/models/validators.py).
- **API Request Construction:**
  - **Name Resolution:** If no key provided, calls `https://api.gbif.org/v1/species/search?q=<name>&status=ACCEPTED&datasetKey=d7dddbf4-2cf0-4f39-9b2a-bb099caae36c`, then uses OpenAI to select best match
  - **Multiple Parallel Calls:**
    - `https://api.gbif.org/v1/species/{key}` (basic info)
    - `https://api.gbif.org/v1/species/{key}/parents` (taxonomic hierarchy)  
    - `https://api.gbif.org/v1/species/{key}/children?limit=20` (child taxa)
    - `https://api.gbif.org/v1/species/{key}/synonyms?limit=20` (synonyms)
- **Response Handling:** Extracts and structures data from multiple endpoints, handles failed endpoints gracefully, creates comprehensive taxonomic artifact
- **Technical Documentation:** [GBIF Species Details API](https://techdocs.gbif.org/en/openapi/v1/species/#/Retrieving%20name%20usages/getNameUsage)
- **Source:** [`find_taxonomic_information.py`](src/entrypoints/species/find_taxonomic_information.py)

Example:
```yaml
Message: 
Parameter:
Response:
```
---

## Parameter Models & Validators
- All parameter models are defined in [`src/models/entrypoints.py`](src/models/entrypoints.py).
- All validators are defined in [`src/models/validators.py`](src/models/validators.py).
- Species parameter enums are in [`src/models/enums/species_parameters.py`](src/models/enums/species_parameters.py).

---

## See Also
- [GBIF API Documentation](https://www.gbif.org/developer/summary)
- [Instructor Documentation](https://github.com/jxnl/instructor)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
