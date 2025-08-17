"""
GBIF Find Occurrence by ID Entrypoint

This entrypoint retrieves a single occurrence record by its GBIF ID using the GBIF occurrences API.
Parameters are provided by the upstream service - no LLM generation needed.
"""

import uuid

from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.entrypoints import GBIFOccurrenceByIdParams
from src.log import with_logging, logger
from src.gbif.parser import parse, GBIFPath


description = """
This entrypoint works against the GBIF Occurrence Store, which handles occurrence records. This entrypoint provides services for retrieving a single occurrence record by its unique GBIF ID.

The returned occurrence includes additional fields, not shown in the response below. They are verbatim fields which are not interpreted by GBIF's system, e.g. `location`. The names are the short Darwin Core Term names.
"""

entrypoint = AgentEntrypoint(
    id="find_occurrence_by_id",
    description="Find occurrence by ID",
    parameters=None,
)


@with_logging("find_occurrence_by_id")
async def run(context: ResponseContext, request: str):
    """
    Executes the occurrence by ID entrypoint. Retrieves a single occurrence record using the provided
    GBIF ID and creates an artifact with the result.
    """
    async with context.begin_process("Requesting GBIF Occurrence by ID") as process:
        AGENT_LOG_ID = f"FIND_OCCURRENCE_BY_ID_{str(uuid.uuid4())[:6]}"
        logger.info(f"GBIF: Agent log ID: {AGENT_LOG_ID}")
        await process.log(
            f"GBIF: Request received: {request}. Generating iChatBio for GBIF request parameters..."
        )

        response = await parse(
            request, GBIFPath.OCCURRENCE_BY_ID, GBIFOccurrenceByIdParams
        )
        params = response.search_parameters
        description = response.artifact_description
        await process.log(
            "GBIF: Generated search parameters",
            data=params.model_dump(exclude_defaults=True),
        )

        api = GbifApi()

        api_url = api.build_occurrence_by_id_url(params)
        await process.log(f"GBIF: Constructed API URL: {api_url}")

        try:
            await process.log("GBIF: Querying GBIF for occurrence data...")
            raw_response = await execute_request(api_url)
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

            portal_url = api.build_portal_url(api_url)

            await process.create_artifact(
                mimetype="application/json",
                description=description,
                uris=[api_url],
                metadata={
                    "portal_url": portal_url,
                    "data_source": "GBIF Occurrence",
                    "data": raw_response,
                },
            )

            summary = _generate_response_summary(params.gbifId, portal_url)
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
                f"I encountered an error while trying to retrieve the occurrence: {str(e)}",
            )


def _generate_response_summary(gbif_id: int, portal_url: str) -> str:
    summary = (
        f"I have successfully retrieved the occurrence record with GBIF ID {gbif_id}. "
    )
    summary += f"The result can also be viewed in the GBIF portal at {portal_url}."
    return summary
