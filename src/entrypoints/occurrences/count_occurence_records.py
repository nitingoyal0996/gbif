"""
GBIF Count Occurrence Records Entrypoint

This entrypoint counts occurrence records and provides faceted statistics using the GBIF occurrences API.
Parameters are provided by the upstream service - no LLM generation needed.
"""

import uuid

from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.entrypoints import GBIFOccurrenceFacetsParams
from src.log import with_logging

from src.gbif.parser import parse, GBIFPath


description = """
This works against the GBIF Occurrence Store, which handles occurrence records. This entrypoint provides services for counting occurrence records with faceted statistics that have been indexed by GBIF.

Counts occurrence records and provides faceted statistics using the GBIF occurrences API. Returns the total
number of records found, breakdown by specified facets, the URL constructed to query the GBIF occurrences API,
and a URL to view the results on the GBIF web portal.

Parameters are provided by the upstream service and include search criteria plus facet specifications:
- Search filters (same as find_occurrence_records)
- Facet fields to analyze (scientificName, country, year, etc.)
- Facet minimum count thresholds
- Facet selection options

Note:
- Year is a 4 digit year. A year of 98 will be interpreted as AD 98. Supports range queries. For instance: year='2020,2023' will return all records from 2020 and 2023.
- Month is the month of the year, starting with 1 for January. Supports range queries. For instance: month='5,12' will return all records from May to December.
"""

entrypoint = AgentEntrypoint(
    id="count_occurrence_records",
    description="Count occurrence records with facets",
    parameters=None,
)


@with_logging("count_occurrence_records")
async def run(context: ResponseContext, request: str):
    """
    Executes the occurrence counting entrypoint. Counts occurrence records using the provided
    parameters and creates an artifact with the faceted results.
    """
    # Generate a unique agent log ID for this run for logging purposes
    AGENT_LOG_ID = f"COUNT_OCCURRENCE_RECORDS_{str(uuid.uuid4())[:6]}"

    async with context.begin_process("Requesting GBIF statistics") as process:
        await process.log(
            f"GBIF: Request recieved: {request}. Generating iChatBio for GBIF request parameters..."
        )
        response = await parse(request, GBIFPath.OCCURRENCE, GBIFOccurrenceFacetsParams)
        params = response.search_parameters
        description = response.artifact_description
        await process.log(
            "GBIF: Generated search and facet parameters: ",
            data=params.model_dump(exclude_defaults=True),
        )

        api = GbifApi()
        api_url = api.build_occurrence_facets_url(params)
        await process.log(f"GBIF: Generated API URL: {api_url}")

        try:
            await process.log(f"GBIF: Sending data retrieval request to {api_url}...")
            raw_response = await execute_request(api_url)
            status_code = raw_response.get("status_code", 200)
            if status_code != 200:
                await process.log(
                    f"GBIF: Data retrieval failed with status code {status_code}",
                    data=raw_response,
                )
                await context.reply(
                    f"Data retrieval failed with status code {status_code}"
                )
                return
            await process.log(
                f"GBIF: Data retrieval successful, status code {status_code}"
            )
            await process.log(f"GBIF: Processing response and preparing artifact...")
            facets = raw_response.get("facets", [])
            total_records = raw_response.get("count", 0)
            portal_url = api.build_portal_url(api_url)
            await process.create_artifact(
                mimetype="application/json",
                description=description,
                uris=[api_url],
                metadata={
                    "portal_url": portal_url,
                    "data_source": "GBIF",
                    "data": raw_response,
                },
            )

            summary = _generate_response_summary(total_records, facets, portal_url)

            await context.reply(summary)

        except Exception as e:
            await process.log(
                f"GBIF: Error during API request",
                data={
                    "error": str(e),
                    "agent_log_id": AGENT_LOG_ID,
                    "api_url": api_url,
                },
            )
            await context.reply(
                f"I encountered an error while trying to count occurrences: {str(e)}",
            )


def _generate_response_summary(
    total_records: int, facets: list[dict], portal_url: str
) -> str:
    if total_records > 0:
        summary = f"I have successfully retrieved {total_records} occurrence records. "
    else:
        summary = f"I have not found any occurrence records matching your criteria. "
    if facets:
        summary += (
            f"Facet fields: {[facet.get('field', 'unknown') for facet in facets]} "
        )
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary
