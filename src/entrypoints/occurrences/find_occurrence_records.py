import uuid

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.entrypoints import GBIFOccurrenceSearchParams
from src.log import with_logging, logger
from src.gbif.parser import parse, GBIFPath
from src.gbif.resolve_parameters import resolve_names_to_taxonkeys


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
        logger.info(f"Agent log ID: {AGENT_LOG_ID}")
        await process.log(
            f"Request recieved: {request}. Generating iChatBio for GBIF request parameters..."
        )
        response = await parse(request, GBIFPath.OCCURRENCE, GBIFOccurrenceSearchParams)
        params = response.search_parameters
        description = response.artifact_description
        await process.log(
            "Generated search parameters",
            data=params.model_dump(exclude_defaults=True),
        )

        api = GbifApi()
        search_params = params

        if params.scientificName:
            await process.log(
                f"Resolving {params.scientificName} scientific names to taxon keys for better search results..."
            )
            taxon_keys = await resolve_names_to_taxonkeys(
                api, params.scientificName, process
            )
            if taxon_keys:
                search_params = await _update_search_params(params, taxon_keys, process)
            else:
                await process.log(
                    "Failed to resolve any scientific names to taxon keys, using original parameters"
                )

        api_url = api.build_occurrence_search_url(search_params)
        await process.log(f"Constructed API URL: {api_url}")

        try:
            await process.log("Querying GBIF for occurrence data...")
            raw_response = await execute_request(api_url)
            status_code = raw_response.get("status_code", 200)
            if status_code != 200:
                await process.log(
                    f"Data retrieval failed with status code {status_code}",
                    data=raw_response,
                )
                await context.reply(
                    f"Data retrieval failed with status code {status_code}",
                )
                return
            await process.log(f"Data retrieval successful, status code {status_code}")
            await process.log("Processing response and preparing artifact...")
            total = raw_response.get("count", 0)
            records = raw_response.get("results", [])
            portal_url = api.build_portal_url(api_url)
            await process.create_artifact(
                mimetype="application/json",
                description=description,
                uris=[api_url],
                metadata={
                    "portal_url": portal_url,
                    "data_source": "GBIF Occurrence",
                },
            )

            summary = _generate_response_summary(total, len(records), portal_url)

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
                f"I encountered an error while trying to search for occurrences: {str(e)}",
            )


def _generate_response_summary(total: int, returned: int, portal_url: str) -> str:
    if total > 0:
        summary = f"I have successfully searched for occurrences and found {total} matching records. "
    else:
        summary = "I have not found any occurrence records matching your criteria. "
    if returned < total:
        summary += f"I've returned {returned} records in this response. out of {total} records."
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary


async def _update_search_params(
    params: GBIFOccurrenceSearchParams,
    taxon_keys: list,
    process: IChatBioAgentProcess,
) -> GBIFOccurrenceSearchParams:
    taxon_key_ints = [int(key) for key in taxon_keys]
    search_params_data = params.model_dump(exclude_defaults=True)
    search_params_data["taxonKey"] = taxon_key_ints
    search_params_data["scientificName"] = None
    search_params = GBIFOccurrenceSearchParams(**search_params_data)
    await process.log(
        f"Created new search parameters with taxon keys: {taxon_key_ints} and preserved other parameters"
    )
    return search_params
