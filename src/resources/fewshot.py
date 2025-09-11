# Few shot examples for entrypoints
examples = {
    "find_occurrence_by_id": [
        {
            "user_request": "Find information on jaguars",
            "search_parameters": None,
            "clarification_needed": True,
            "clarification_reason": "To search for a specific species like 'jaguar,' I need its unique GBIF identifier to use this entrypoint.",
        },
        {
            "user_request": "Find information on 1234567890",
            "search_parameters": {"occurrenceId": "1234567890"},
            "clarification_needed": False,
            "clarification_reason": None,
        },
    ],
    "find_occurrence_records": [
        {
            "user_request": "Find occurrences of jaguars",
            "search_parameters": None,
            "clarification_needed": True,
            "clarification_reason": "I need either scientificName or taxonKey to search for occurrences.",
        },
        {
            "user_request": "Find occurrences of Panthera onca in the US",
            "search_parameters": {"scientificName": "Panthera onca", "country": "US"},
            "clarification_needed": False,
            "clarification_reason": None,
        },
        {
            "user_request": "Find occurrences of Panthera onca in the Plam Spring, CA in 2020",
            "search_parameters": None,
            "clarification_needed": True,
            "clarification_reason": "I need latitude and longitude of Plam Spring, CA to search for occurrences.",
        },
    ],
    "count_occurrence_records": [
        {
            "user_request": "Give me a count of all records by basis of record.",
            "search_parameters": {"facet": ["basisOfRecord"]},
            "clarification_needed": False,
            "clarification_reason": None,
        },
        {
            "user_request": "For all Panthera onca records in the US, what's the breakdown by year?",
            "search_parameters": {"scientificName": "Panthera onca", "country": "US", "facet": ["year"]},
            "clarification_needed": False,
            "clarification_reason": None,
        },
        {
            "user_request": "Break down the records by observer.",
            "search_parameters": None,
            "clarification_needed": True,
            "clarification_reason": "I can create a breakdown by specific fields like 'recordedBy', 'country', or 'year'. Could you please clarify which field you'd like to use?",
        },
    ],
    "find_species_records": [
        {
            "user_request": "Look up the species 'jaguar'",
            "search_parameters": None,
            "clarification_needed": True,
            "clarification_reason": "To ensure I search correctly, should I treat 'jaguar' as a common (vernacular) name or a scientific name?",
        },
        {
            "user_request": "Find all endangered species of Panthera onca (scientific name)",
            "search_parameters": {"q": "Panthera onca", "threat": "ENDANGERED", "qField": "SCIENTIFIC_NAME"},
            "clarification_needed": False,
            "clarification_reason": None,
        }
    ],
    "find_species_taxonomic_information": [
        {
            "user_request": "Get taxonomic information for species with id 5231190",
            "search_parameters": {"key": 5231190},
            "clarification_needed": False,
            "clarification_reason": None,
        },
        {
            "user_request": "child and parent taxa of Panthera onca",
            "search_parameters": {"key": 5231190, "includeChildren": True, "includeParents": True},
            "clarification_needed": False,
            "clarification_reason": None
        },
    ],
    "count_species_records": [
        {
            "user_request": "Give me a count of all species by rank.",
            "search_parameters": {"facet": ["rank"]},
            "clarification_needed": False,
            "clarification_reason": None,
        },
        {
            "user_request": "Give me a count of all species by location.",
            "search_parameters": None,
            "clarification_needed": True,
            "clarification_reason": "'Location' is too general for a statistical breakdown. I can count species by supported fields like `habitat`, `threat` status, or taxonomic `rank`. Which of these would you like to use?",
        },
    ],
}
