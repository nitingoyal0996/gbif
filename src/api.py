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
)


class GbifApi:
    """GBIF API interaction logic."""

    def __init__(self):
        self.base_url = "https://api.gbif.org/v1"
        self.portal_url = "https://gbif.org"
        self.config = {
            "timeout": 30,
            "max_retries": 3
        }

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
        """Build URL for occurrence search."""
        api_params = self._convert_to_api_params(params)
        query_string = urlencode(api_params, doseq=True)
        return f"{self.base_url}/occurrence/search?{query_string}"

    def build_occurrence_facets_url(self, params: GBIFOccurrenceFacetsParams) -> str:
        """Build URL for occurrence facets search."""
        api_params = self._convert_to_api_params(params)
        query_string = urlencode(api_params, doseq=True)
        return f"{self.base_url}/occurrence/search?{query_string}"

    def build_species_search_url(self, params: GBIFSpeciesSearchParams) -> str:
        """Build URL for species search."""
        api_params = self._convert_to_api_params(params)
        query_string = urlencode(api_params, doseq=True)
        return f"{self.base_url}/species/search?{query_string}"

    def build_species_facets_url(self, params: GBIFSpeciesFacetsParams) -> str:
        """Build URL for species facets search."""
        api_params = self._convert_to_api_params(params)
        query_string = urlencode(api_params, doseq=True)
        return f"{self.base_url}/species/search?{query_string}"

    def build_portal_url(self, api_url: str) -> str:
        """Convert API URL to portal URL."""
        if "/occurrence/search?" in api_url:
            return api_url.replace(self.base_url, self.portal_url)
        elif "/species/search?" in api_url:
            return api_url.replace(self.base_url, self.portal_url)
        return api_url

    def execute_sync_request(self, url: str) -> Dict[str, Any]:
        """Execute synchronous HTTP request."""
        response = requests.get(url, timeout=self.config["timeout"])
        response.raise_for_status()
        return response.json()

    async def execute_request(self, url: str) -> Dict[str, Any]:
        """Execute asynchronous HTTP request."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute_sync_request, url)

    def format_response_summary(self, response_data: Dict[str, Any]) -> str:
        """Format response data into a human-readable summary."""
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
