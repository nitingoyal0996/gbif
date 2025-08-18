import uuid

from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.entrypoints import GBIFSpeciesSearchParams
from src.log import with_logging, logger
from src.gbif.parser import parse, GBIFPath


description = """
This entrypoint works against data kept in the GBIF Checklist Bank which taxonomically indexes all registered checklist datasets in the GBIF network. And it provides services for full-text search of name usages covering the scientific and vernacular names, the species description, distribution and the entire classification across all name usages of all or some checklists. Results are ordered by relevance as this search usually returns a lot of results.
"""

entrypoint = AgentEntrypoint(
    id="find_species_records",
    description="Search species name usages",
    parameters=None,
)


@with_logging("find_species_records")
async def run(context: ResponseContext, request: str):
    """
    Executes the species search entrypoint. Searches for species name usages using the provided
    parameters and creates an artifact with the results.
    """
    async with context.begin_process("Requesting GBIF Species Records") as process:
        AGENT_LOG_ID = f"FIND_SPECIES_RECORDS_{str(uuid.uuid4())[:6]}"
        logger.info(f"Agent log ID: {AGENT_LOG_ID}")
        await process.log(
            f"Request received: {request}. Generating iChatBio for GBIF request parameters..."
        )

        response = await parse(request, GBIFPath.SPECIES, GBIFSpeciesSearchParams)
        params = response.search_parameters
        description = response.artifact_description
        await process.log(
            "Generated search parameters",
            data=params.model_dump(exclude_defaults=True),
        )

        api = GbifApi()

        api_url = api.build_species_search_url(params)
        await process.log(f"Constructed API URL: {api_url}")

        try:
            await process.log("Querying GBIF for species data...")
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

            total = raw_response.get('count', 0)
            records = raw_response.get("results", [])
            portal_url = api.build_portal_url(api_url)

            await process.create_artifact(
                mimetype="application/json",
                description=description,
                uris=[api_url],
                metadata={
                    "portal_url": portal_url,
                    "data_source": "GBIF Species",
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
                f"I encountered an error while trying to search for species: {str(e)}",
            )


def _generate_response_summary(total: int, returned: int, portal_url: str) -> str:
    if total > 0:
        summary = f"I have successfully searched for species and found {total} matching name usage records. "
    else:
        summary = "I have not found any species records matching your criteria. "
    if returned < total:
        summary += f"I've returned {returned} records in this response. "
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary
