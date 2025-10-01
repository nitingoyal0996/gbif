"""
GBIF API URL Builder Module
"""

from typing import Dict, Any
from urllib.parse import urlencode

from src.models.entrypoints import (
    GBIFOccurrenceSearchParams,
    GBIFOccurrenceFacetsParams,
    GBIFSpeciesSearchParams,
    GBIFSpeciesFacetsParams,
    GBIFSpeciesTaxonomicParams,
    GBIFOccurrenceByIdParams,
    GBIFDatasetSearchParams,
)


class GbifApi:
    def __init__(self):
        self.base_url = "https://api.gbif.org/v1"
        self.v2_base_url = "https://api.gbif.org/v2"
        self.portal_url = "https://gbif.org"

    def _convert_to_api_params(self, params) -> Dict[str, Any]:
        api_params = {}

        for field_name, value in params.model_dump().items():
            if value is None:
                continue

            if isinstance(value, list):
                processed_values = []
                for item in value:
                    if hasattr(item, "value"):
                        processed_values.append(item.value)
                    elif isinstance(item, bool):
                        processed_values.append(str(item).lower())
                    else:
                        processed_values.append(item)
                api_params[field_name] = processed_values
            elif hasattr(value, "value"):
                api_params[field_name] = value.value
            elif isinstance(value, bool):
                api_params[field_name] = str(value).lower()
            else:
                api_params[field_name] = value

        return api_params

    def build_occurrence_search_url(self, params: GBIFOccurrenceSearchParams) -> str:
        api_params = self._convert_to_api_params(params)
        query_string = urlencode(api_params, doseq=True)
        return f"{self.base_url}/occurrence/search?{query_string}"

    def build_occurrence_facets_url(self, params: GBIFOccurrenceFacetsParams) -> str:
        api_params = self._convert_to_api_params(params)
        api_params["limit"] = 0
        query_string = urlencode(api_params, doseq=True)
        return f"{self.base_url}/occurrence/search?{query_string}"

    def build_species_search_url(self, params: GBIFSpeciesSearchParams) -> str:
        api_params = self._convert_to_api_params(params)
        query_string = urlencode(api_params, doseq=True)
        return f"{self.base_url}/species/search?{query_string}"

    def build_species_facets_url(self, params: GBIFSpeciesFacetsParams) -> str:
        api_params = self._convert_to_api_params(params)
        api_params["limit"] = 0
        query_string = urlencode(api_params, doseq=True)
        return f"{self.base_url}/species/search?{query_string}"

    def build_species_key_search_url(self, usage_key: int) -> str:
        base_url = f"{self.base_url}/species/{usage_key}"
        return base_url

    def build_species_taxonomic_urls(
        self, params: GBIFSpeciesTaxonomicParams
    ) -> Dict[str, str]:
        usage_key = params.key
        base_url = self.build_species_key_search_url(usage_key)
        urls = {
            "basic": f"{base_url}",
            "parsed_name": f"{base_url}/name",
        }
        if params.includeParents:
            urls["parents"] = f"{base_url}/parents"
        if params.includeChildren:
            urls["children"] = (
                f"{base_url}/children?limit={params.limit}&offset={params.offset}"
            )
        if params.includeSynonyms:
            urls["synonyms"] = (
                f"{base_url}/synonyms?limit={params.limit}&offset={params.offset}"
            )
        return urls

    def build_species_match_url(self, scientific_name: str) -> str:
        base_url = f"{self.v2_base_url}/species/match"
        params = {"scientificName": scientific_name}
        query_string = urlencode(params, doseq=True)
        return f"{base_url}?{query_string}"

    def build_occurrence_by_id_url(self, params: GBIFOccurrenceByIdParams) -> str:
        gbif_id = params.gbifId
        base_url = f"{self.base_url}/occurrence/{gbif_id}"
        return base_url

    def build_dataset_search_url(self, params: GBIFDatasetSearchParams) -> str:
        api_params = self._convert_to_api_params(params)
        query_string = urlencode(api_params, doseq=True)
        return f"{self.base_url}/dataset/search?{query_string}"

    def build_portal_url(self, api_url: str) -> str:
        """Convert an API URL to its corresponding portal URL by removing facet parameters."""
        # Split URL into base and query string
        base_part, *query_part = api_url.split("?")

        # Replace API base URL with portal URL base
        portal_base = base_part.replace(self.base_url, self.portal_url)

        # If no query parameters, return just the base
        if not query_part:
            return portal_base

        # Parse query string into dictionary
        from urllib.parse import parse_qs

        params = parse_qs(query_part[0])

        # Remove facet-related and limit=0 parameters
        params_to_remove = [
            "limit",
            "facet",
            "facetLimit",
            "facetOffset",
            "facetMinCount",
            "facetMultiselect",
        ]
        for param in params_to_remove:
            params.pop(param, None)

        # Reconstruct query string from remaining parameters
        if params:
            query_string = "&".join(
                f"{key}={value[0]}" if len(value) == 1 else f"{key}={','.join(value)}"
                for key, value in params.items()
            )
            return f"{portal_base}?{query_string}"

        return portal_base
