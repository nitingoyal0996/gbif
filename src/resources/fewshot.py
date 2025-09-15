examples = {
    "find_occurrence_by_id": [
        {
            "response": {
                "user_request": "Find information on jaguars",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "To search for a specific occurrence by ID, I need the unique GBIF occurrence identifier (gbifId). 'Jaguars' appears to be a species name, not a numeric occurrence ID.",
            },
            "reasoning": "This endpoint requires a single numeric `gbifId` parameter. The user provided 'jaguars' which is a species name (string), not a numeric occurrence identifier. The parameter types are incompatible, so clarification is mandatory.",
        },
        {
            "response": {
                "user_request": "Get details for occurrence 1234567890",
                "search_parameters": {"gbifId": 1234567890},
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "User provided 'occurrence 1234567890' where 1234567890 is clearly a numeric identifier matching the required `gbifId` parameter type. The request is unambiguous and complete.",
        },
        {
            "response": {
                "user_request": "Show me record abc123",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "'abc123' appears to be an alphanumeric identifier, but this endpoint requires a numeric GBIF occurrence ID (gbifId). Please provide the numeric GBIF occurrence identifier.",
            },
            "reasoning": "The identifier 'abc123' is alphanumeric, but `gbifId` must be numeric. This is a type mismatch requiring clarification to get the correct numeric identifier.",
        },
    ],
    "find_occurrence_records": [
        {
            "response": {
                "user_request": "Find occurrences of jaguars",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "'Jaguars' could be a common name. I need either the exact scientific name (e.g., 'Panthera onca') or a numeric taxonKey to search occurrences accurately.",
            },
            "reasoning": "The term 'jaguars' is ambiguous - it's likely a common name rather than a scientific name. Per the literal identifier rules, I cannot guess the scientificName or taxonKey. The user must provide the exact scientific name or numeric taxon identifier.",
        },
        {
            "response": {
                "user_request": "Find occurrences of Panthera onca in Brazil from 2020-2022",
                "search_parameters": {
                    "scientificName": ["Panthera onca"],
                    "country": ["BR"],
                    "year": "2020,2022",
                },
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "User provided exact scientific name 'Panthera onca', clear country 'Brazil' (transforms to ISO code 'BR'), and specific year range. All required information is present and transformable to API format.",
        },
        {
            "response": {
                "user_request": "Show me bird sightings in Miami-Dade County",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "I need clarification on two points: 1) 'Birds' is too general - please provide a specific scientific name or taxonKey, and 2) 'Miami-Dade County' requires specific coordinates (decimalLatitude, decimalLongitude) and search radius for geographic filtering.",
            },
            "reasoning": "Two issues: 'birds' lacks specificity for taxonomic search, and 'Miami-Dade County' is more specific than supported geographic parameters (country/state level). Both require clarification per the geographic and literal identifier rules.",
        },
        {
            "response": {
                "user_request": "Find Quercus robur specimens with coordinates between 2010 and 2015",
                "search_parameters": {
                    "scientificName": ["Quercus robur"],
                    "basisOfRecord": ["PRESERVED_SPECIMEN"],
                    "hasCoordinate": True,
                    "year": "2010,2015",
                },
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "Clear scientific name provided, 'specimens' maps to PRESERVED_SPECIMEN basis of record, 'with coordinates' maps to hasCoordinate=true, and year range is clearly specified. All parameters are deterministic.",
        },
        {
            "response": {
                "user_request": "Get occurrence records with taxon key 2476674 in European countries",
                "search_parameters": {"taxonKey": [2476674], "continent": ["EUROPE"]},
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "Specific numeric taxonKey provided (matches literal identifier requirement) and 'European countries' clearly maps to continent parameter. Request is complete and unambiguous.",
        },
    ],
    "count_occurrence_records": [
        {
            "response": {
                "user_request": "Count all jaguar records by country",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "I need the exact scientific name or taxonKey for 'jaguar'. Additionally, please confirm if you want to facet by 'country' field for the breakdown.",
            },
            "reasoning": "Two issues: 'jaguar' lacks scientific precision (literal identifier rule), and while 'by country' likely means facet=['country'], I should confirm the faceting parameter due to the importance of accurate aggregation.",
        },
        {
            "response": {
                "user_request": "Give me occurrence counts for Panthera onca faceted by basisOfRecord and year",
                "search_parameters": {
                    "scientificName": ["Panthera onca"],
                    "facet": ["basisOfRecord", "year"],
                    "limit": 0,
                },
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "Scientific name is exact, facet parameters are explicitly named, and this is clearly a count request (limit=0 for facets only). All requirements are met with no ambiguity.",
        },
        {
            "response": {
                "user_request": "Break down records by observer in Costa Rica",
                "search_parameters": {
                    "country": ["CR"],
                    "facet": ["recordedBy"],
                    "limit": 0,
                },
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "'Observer' clearly maps to 'recordedBy' field, 'Costa Rica' transforms to country code 'CR', and 'break down' indicates faceting. The mapping is deterministic.",
        },
    ],
    "find_species_records": [
        {
            "response": {
                "user_request": "Search for jaguar species",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "Should I search for 'jaguar' as a vernacular/common name or as a scientific name? This affects whether I use qField='VERNACULAR_NAME' or qField='SCIENTIFIC_NAME'.",
            },
            "reasoning": "'Jaguar' could be interpreted as either a common name or part of a scientific name. The qField parameter significantly affects search results, so clarification is essential for accuracy.",
        },
        {
            "response": {
                "user_request": "Find all endangered Panthera species",
                "search_parameters": {
                    "q": "Panthera",
                    "threat": "ENDANGERED",
                    "qField": "SCIENTIFIC_NAME",
                },
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "'Panthera' is clearly a scientific genus name, 'endangered' maps directly to threat status, and the search intent is clear. All parameters can be confidently determined.",
        },
        {
            "response": {
                "user_request": "Show me all cats",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "'Cats' is too vague - it could refer to the family Felidae, domestic cats (Felis catus), or be a colloquial term. Please provide a more specific scientific name or clarify the taxonomic scope.",
            },
            "reasoning": "'Cats' is highly ambiguous and could refer to multiple taxonomic levels or common usage. Without scientific precision, the search would be unreliable.",
        },
    ],
    "find_species_taxonomic_information": [
        {
            "response": {
                "user_request": "Get taxonomy for species 5231190",
                "search_parameters": {"key": 5231190},
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "Numeric identifier '5231190' clearly matches the required 'key' parameter type. Request is unambiguous and complete.",
        },
        {
            "response": {
                "user_request": "Show full classification hierarchy for Panthera onca including synonyms",
                "search_parameters": {
                    "name": "Panthera onca",
                    "includeSynonyms": True,
                    "includeParents": True,
                },
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "Scientific name is provided exactly, 'synonyms' maps to includeSynonyms=True, 'classification hierarchy' indicates includeParents=True. All intent is clear and mappable.",
        },
        {
            "response": {
                "user_request": "Get taxonomic info for the big cat from South America",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "'Big cat from South America' is descriptive but not specific enough. I need either a numeric species key or the exact scientific name to retrieve taxonomic information.",
            },
            "reasoning": "Descriptive phrase doesn't provide the required literal identifiers (key or scientific name). Multiple species could match this description, violating the precision requirement.",
        },
    ],
    "find_datasets": [
        {
            "response": {
                "user_request": "Find marine biodiversity datasets from European institutions",
                "search_parameters": {
                    "q": "marine biodiversity",
                    "continent": "EUROPE",
                },
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "'Marine biodiversity' is a clear keyword search term, and 'European institutions' maps to continent filter. Both parameters are well-defined.",
        },
        {
            "response": {
                "user_request": "Show me the most comprehensive datasets about birds",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "I cannot rank datasets by 'comprehensiveness' as this is subjective. I can search for bird-related datasets using keywords, but please specify search criteria like dataset type, geographic scope, or specific keywords.",
            },
            "reasoning": "'Most comprehensive' is a subjective ranking criterion not supported by the API. The system needs objective search parameters rather than qualitative assessments.",
        },
        {
            "response": {
                "user_request": "Find occurrence datasets that are also specimen collections",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "Dataset type can only be one value (OCCURRENCE, CHECKLIST, etc.). Did you mean occurrence datasets that contain specimen records, or are you looking for a specific dataset subtype?",
            },
            "reasoning": "The 'type' parameter accepts only one value, so datasets cannot be both OCCURRENCE and another type simultaneously. This represents a logical constraint violation requiring clarification.",
        },
    ],
    "count_species_records": [
        {
            "response": {
                "user_request": "Count species by kingdom",
                "search_parameters": {"facet": ["kingdom"]},
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "The user wants a count of species grouped by kingdom, which maps to a facet search on the 'kingdom' field.",
        },
        {
            "response": {
                "user_request": "How many endangered species are there?",
                "search_parameters": {"threat": "ENDANGERED"},
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "The user wants a count of species with threat status 'ENDANGERED'. This maps directly to the 'threat' parameter.",
        },
    ],
}
