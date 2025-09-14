# Few shot examples for entrypoints
# These can be refined to be more specific to how
# iChatBio provides the request to the entrypoint
examples = {
    "find_occurrence_by_id": [
        {
            "response": {
                "user_request": "Find information on jaguars",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "To search for a specific species like 'jaguar,' I need its unique GBIF identifier to use this entrypoint.",
            },
            "reasoning": "This tool requires a single numeric `gbifId`. The user provided a value ('jaguars') which is a string/name and does not match with any required parameter. The necessary input is missing, so I must ask for clarification.",
        },
        {
            "response": {
                "user_request": "Find information on 1234567890",
                "search_parameters": {"gbifId": "1234567890"},
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "This tool requires a single numeric `gbifId`. The user provided a value ('1234567890') whose type (a long number) matches the model type. This allows me to confidently populate the `gbifId` parameter.",
        },
    ],
    "find_occurrence_records": [
        {
            "response": {
                "user_request": "Find occurrences of jaguars",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "I need either an exact scientificName or a taxonKey to search for occurrences.",
            },
            "reasoning": "'Jaguars' does not seem like a `scientificName`. Further, there is no `taxonKey` provided in the reqquest. Since the input parameters are either not clear or missing, I must ask for clarification.",
        },
        {
            "response": {
                "user_request": "Find occurrences of jaguar (Panthera onca) in the United States",
                "search_parameters": {
                    "scientificName": "Panthera onca",
                    "country": "US",
                },
                "clarification_needed": False,
                "clarification_reason": None,
            },
            "reasoning": "User is asking for records of Jaguar, while this seems like a common name, name - Panthera onca - in the bracket seems like a scientific name. The user provided an exact `scientificName` ('Panthera onca') and a valid `country` parameter value United States which corresponds to the ISO 3166-1 code 'US'. So, I don't need more assistance to generate the search parameters.",
        },
        {
            "response": {
                "user_request": "Find occurrences of Panthera onca in Palm Springs, CA in 2020",
                "search_parameters": None,
                "clarification_needed": True,
                "clarification_reason": "I need the latitude and longitude for 'Palm Springs, CA' to search in such a specific area. If coordinates are not available, please ask to use `locality` parameter instead",
            },
            "reasoning": "The tool can filter by broad regions like `country` or `stateProvince`, but a precise location like a city requires numeric `latitude` and `longitude` parameters. The user provided a place name ('Palm Springs, CA') but not the required coordinates for this type of search. So, I must ask for clarification.",
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
            "user_request": "For all jaguar (Panthera onca) records in the US, what's the breakdown by year?",
            "search_parameters": {
                "scientificName": "Panthera onca",
                "country": "US",
                "facet": ["year"],
            },
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
            "user_request": "Find all endangered species of Panthera onca (jaguar)",
            "search_parameters": {
                "q": "Panthera onca",
                "threat": "ENDANGERED",
                "qField": "SCIENTIFIC_NAME",
            },
            "clarification_needed": False,
            "clarification_reason": None,
        },
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
            "search_parameters": {
                "key": 5231190,
                "includeChildren": True,
                "includeParents": True,
            },
            "clarification_needed": False,
            "clarification_reason": None,
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
    "find_datasets": [
        {
            "user_request": "Search for datasets about marine biodiversity from Europe.",
            "search_parameters": {"q": "marine biodiversity", "continent": "EUROPE"},
            "clarification_needed": False,
            "clarification_reason": None,
        },
        {
            "user_request": "Show me all checklist datasets from the US.",
            "search_parameters": {"type": "CHECKLIST", "publishingCountry": "US"},
            "clarification_needed": False,
            "clarification_reason": None,
        },
        {
            "user_request": "Find datasets about migration.",
            "search_parameters": None,
            "clarification_needed": True,
            "clarification_reason": "The keyword 'migration' is ambiguous. To get relevant results, please provide more specific criteria, such as a particular species (e.g., 'bird migration'), a geographic area, or another keyword.",
        },
        {
            "user_request": "Find the most popular datasets about insects.",
            "search_parameters": None,
            "clarification_needed": True,
            "clarification_reason": "I can't sort or rank datasets by 'popularity'. However, I can search for datasets using keywords or filter by criteria like the data type or publishing country.",
        },
        {
            "user_request": "Show me the most interesting datasets.",
            "search_parameters": None,
            "clarification_needed": True,
            "clarification_reason": "The term 'interesting' is subjective and I can't search for it directly. Could you please provide more concrete search criteria, such as a specific topic, keyword, or geographic area?",
        },
        {
            "user_request": "Find me all checklist datasets that are also occurrence datasets.",
            "search_parameters": None,
            "clarification_needed": True,
            "clarification_reason": "A dataset can only have one primary type at a time. Could you please clarify whether you are looking for 'checklist' datasets or 'occurrence' datasets?",
        },
    ],
}
