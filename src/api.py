"""
GBIF Logic Module

Handles API interactions with the GBIF occurrences API, URL construction, and response formatting.
"""

import asyncio
import requests
from typing import Dict, Any
from urllib.parse import urlencode

from src.models.entrypoints import (
    GBIFOccurrenceSearchParams,
    GBIFOccurrenceFacetsParams,
    GBIFSpeciesSearchParams,
    GBIFSpeciesFacetsParams,
    GBIFSpeciesTaxonomicParams,
)


class GbifApi:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GbifApi, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.base_url = "https://api.gbif.org/v1"
        self.portal_url = "https://gbif.org"
        self.config = {
            "timeout": 30,
            "max_retries": 3
        }
        self._initialized = True

    def _convert_to_api_params(self, params) -> Dict[str, Any]:
        """Convert Pydantic model to API parameters, handling enums properly."""
        api_params = {}

        for field_name, value in params.model_dump(exclude_defaults=True).items():
            if value is None:
                continue

            # Handle enum values - extract the actual value
            if isinstance(value, list):
                # Handle lists of enums or regular values
                processed_values = []
                for item in value:
                    if hasattr(item, 'value'):
                        processed_values.append(item.value)
                    else:
                        processed_values.append(item)
                api_params[field_name] = processed_values
            elif hasattr(value, 'value'):
                # Handle single enum value
                api_params[field_name] = value.value
            else:
                # Handle regular values
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

    def build_portal_url(self, api_url: str) -> str:
        if "/occurrence/search?" in api_url:
            return api_url.replace(self.base_url, self.portal_url)
        elif "/species/search?" in api_url:
            return api_url.replace(self.base_url, self.portal_url)
        return api_url

    def execute_sync_request(self, url: str) -> Dict[str, Any]:
        response = requests.get(url, timeout=self.config["timeout"])
        response.raise_for_status()
        return response.json()

    async def execute_request(self, url: str) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute_sync_request, url)

    async def execute_multiple_requests(self, urls: Dict[str, str]) -> Dict[str, Any]:
        """Execute multiple API requests concurrently and return combined results."""
        tasks = []
        for endpoint_name, url in urls.items():
            tasks.append(self.execute_request(url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined_results = {}
        for endpoint_name, result in zip(urls.keys(), results):
            if isinstance(result, Exception):
                combined_results[endpoint_name] = {"error": str(result)}
            else:
                combined_results[endpoint_name] = result

        return combined_results

    def format_response_summary(self, response_data: Dict[str, Any]) -> str:
        if not response_data:
            return "No data returned"

        count = response_data.get('count', 0)
        results = response_data.get('results', [])

        if count == 0:
            return "No records found"
        elif not results:
            return f"Found {count} total records"
        else:
            return f"Found {count} total records (returned {len(results)})" 
