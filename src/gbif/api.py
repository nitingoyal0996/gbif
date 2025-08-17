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

        for field_name, value in params.model_dump(exclude_defaults=True).items():
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

    def build_species_taxonomic_urls(
        self, params: GBIFSpeciesTaxonomicParams
    ) -> Dict[str, str]:
        usage_key = params.key
        base_url = f"{self.base_url}/species/{usage_key}"
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
        portal_url = self.portal_url
        if "/occurrence/search?" in api_url:
            portal_url = api_url.replace(self.base_url, self.portal_url)
        elif "/species/search?" in api_url:
            portal_url = api_url.replace(self.base_url, self.portal_url)
        elif "/occurrence/" in api_url and not "?" in api_url:
            portal_url = api_url.replace(self.base_url, self.portal_url)
        elif "/dataset/search?" in api_url:
            portal_url = api_url.replace(self.base_url, self.portal_url)
        portal_url = portal_url.replace("&limit=0", "")
        portal_url = portal_url.replace("?limit=0", "")
        return portal_url
