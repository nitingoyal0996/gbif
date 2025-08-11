"""
GBIF Find Occurrence Records Entrypoint

This entrypoint searches for species occurrence records using the GBIF occurrences API.
Parameters are provided by the upstream service - no LLM generation needed.
"""
import uuid

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.api import GbifApi
from src.models.entrypoints import GBIFOccurrenceSearchParams
from src.log import with_logging, logger
from src.parser import parse, GBIFPath


description = """
This entrypoint works against the GBIF Occurrence Store, which handles occurrence records. This entrypoint provides services for searching occurrence records that have been indexed by GBIF.

Note:
- Year is a 4 digit year. A year of 98 will be interpreted as AD 98. Supports range queries. For instance: year='2020,2023' will return all records from 2020 and 2023.
- Month is the month of the year, starting with 1 for January. Supports range queries. For instance: month='5,12' will return all records from May to December.
"""

entrypoint = AgentEntrypoint(
    id="find_occurrence_records",
    description="Find occurrence records",
    parameters=None,
)


@with_logging("find_occurrence_records")
async def run(context: ResponseContext, request: str):
    """
    Executes the occurrence search entrypoint. Searches for occurrence records using the provided
    parameters and creates an artifact with the results.
    """

    async with context.begin_process("Requesting GBIF Occurrence Records") as process:
        AGENT_LOG_ID = f"FIND_OCCURRENCE_RECORDS_{str(uuid.uuid4())[:6]}"
        logger.info(f"GBIF: Agent log ID: {AGENT_LOG_ID}")
        await process.log(
            f"GBIF: Request recieved: {request}. Generating iChatBio for GBIF request parameters..."
        )
        response = await parse(request, GBIFPath.OCCURRENCE, GBIFOccurrenceSearchParams)
        params = response.search_parameters
        description = response.artifact_description
        await process.log(
            "GBIF: Generated search parameters",
            data=params.model_dump(exclude_defaults=True),
        )

        gbif_api = GbifApi()
        api_url = gbif_api.build_occurrence_search_url(params)
        await process.log(f"GBIF: Constructed API URL: {api_url}")

        try:
            await process.log("GBIF: Querying GBIF for occurrence data...")
            raw_response = await gbif_api.execute_request(api_url)
            status_code = raw_response.get("status_code", 200)
            if status_code != 200:
                await process.log(
                    f"GBIF: Data retrieval failed with status code {status_code}",
                    data=raw_response,
                )
                await context.reply(
                    f"Data retrieval failed with status code {status_code}",
                )
                return
            await process.log(
                f"GBIF: Data retrieval successful, status code {status_code}"
            )
            await process.log(f"GBIF: Processing response and preparing artifact...")
            total = raw_response.get("count", 0)
            records = raw_response.get("results", [])
            portal_url = gbif_api.build_portal_url(api_url)
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

            summary = _generate_response_summary(total, len(records), portal_url)

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
                f"I encountered an error while trying to search for occurrences: {str(e)}",
            )


def _generate_response_summary(total: int, returned: int, portal_url: str) -> str:
    if total > 0:
        summary = f"I have successfully searched for occurrences and found {total} matching records. "
    else:
        summary = f"I have not found any occurrence records matching your criteria. "
    if returned < total:
        summary += f"I've returned {returned} records in this response. "
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary
