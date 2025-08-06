"""
GBIF Species Search Entrypoint

This entrypoint searches for species name usages using the GBIF species API.
Provides full-text search over name usages covering scientific and vernacular names,
species descriptions, distribution and classification data.
"""
import uuid

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.api import GbifApi
from src.models.entrypoints import GBIFSpeciesSearchParams
from src.log import with_logging

from src.parser import parse, GBIFPath


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
    # Generate a unique agent log ID for this run for logging purposes
    AGENT_LOG_ID = f"FIND_SPECIES_RECORDS_{str(uuid.uuid4())[:6]}"

    await context.reply("Parsing request parameters using LLM...")
    response = await parse(request, GBIFPath.SPECIES, GBIFSpeciesSearchParams)
    params = response.search_parameters
    description = response.artifact_description

    async with context.begin_process("Searching GBIF species database") as process:
        process: IChatBioAgentProcess
        await process.log(f"Agent log ID: {AGENT_LOG_ID}")
        await process.log(
            "Search parameters", data=params.model_dump(exclude_defaults=True)
        )

        gbif_api = GbifApi()
        api_url = gbif_api.build_species_search_url(params)
        await process.log(f"Constructed API URL: {api_url}")

        try:
            await process.log("Querying GBIF for species data...")
            raw_response = await gbif_api.execute_request(api_url)

            total = raw_response.get('count', 0)
            records = raw_response.get("results", [])
            returned = len(records)

            await process.log(f"Query successful, found {total} species records.")
            await process.create_artifact(
                mimetype="application/json",
                description=description,
                uris=[api_url],
                metadata={
                    "data_source": "GBIF Species",
                    "data": records,
                    "record_count": returned,
                    "portal_url": gbif_api.build_portal_url(api_url),
                },
            )

            summary = f"I have successfully searched for species and found {total} matching name usage records. "
            if returned < total:
                summary += f"I've returned {returned} records in this response. "
            summary += f"The results can be viewed in the GBIF portal at {gbif_api.build_portal_url(api_url)}."

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
            await context.reply(f"I encountered an error while trying to search for species: {str(e)}") 
