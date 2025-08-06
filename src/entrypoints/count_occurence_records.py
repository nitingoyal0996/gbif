"""
GBIF Count Occurrence Records Entrypoint

This entrypoint counts occurrence records and provides faceted statistics using the GBIF occurrences API.
Parameters are provided by the upstream service - no LLM generation needed.
"""

import uuid
from typing import Optional

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.api import GbifApi
from src.models.entrypoints import GBIFOccurrenceFacetsParams
from src.log import with_logging

from src.parser import parse, GBIFPath


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

    await context.reply("Parsing request parameters using LLM...")
    response = await parse(request, GBIFPath.OCCURRENCE, GBIFOccurrenceFacetsParams)
    params = response.search_parameters
    description = response.artifact_description

    async with context.begin_process(
        "Counting GBIF occurrence records with facets"
    ) as process:
        process: IChatBioAgentProcess
        await process.log(f"Agent log ID: {AGENT_LOG_ID}")
        await process.log(
            "Search and facet parameters", data=params.model_dump(exclude_defaults=True)
        )

        gbif = GbifApi()
        api_url = gbif.build_occurrence_facets_url(params)
        await process.log(f"Constructed API URL: {api_url}")

        try:
            await process.log("Querying GBIF for occurrence statistics...")
            raw_response = await gbif.execute_request(api_url)

            facets = raw_response.get("facets", [])
            returned = len(facets)

            await process.log(
                f"Query successful, found {returned} records with {len(facets)} facet groups."
            )
            await process.create_artifact(
                mimetype="application/json",
                description=description,
                uris=[api_url],
                metadata={
                    "data_source": "GBIF Occurrences",
                    "data": facets,
                    "portal_url": gbif.build_portal_url(api_url),
                },
            )

            summary = f"I have successfully counted occurrences and found {total} matching records. "
            if facets:
                facet_summary = ", ".join(
                    [
                        f"{facet.get('field', 'unknown')} ({len(facet.get('counts', []))} values)"
                        for facet in facets
                    ]
                )
                summary += f"The results are broken down by: {facet_summary}. "
            summary += f"The results can be viewed in the GBIF portal at {gbif.build_portal_url(api_url)}."

            await context.reply(summary)

        except Exception as e:
            await process.log(
                "Error during API request",
                data={
                    "error": str(e),
                    "agent_log_id": AGENT_LOG_ID,
                    "api_url": api_url,
                },
            )
            await context.reply(
                f"I encountered an error while trying to count occurrences: {str(e)}"
            )
