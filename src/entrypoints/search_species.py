"""
GBIF Species Search Entrypoint

This entrypoint searches for species name usages using the GBIF species API.
Provides full-text search over name usages covering scientific and vernacular names,
species descriptions, distribution and classification data.
"""
import uuid
from typing import Optional

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.api import GbifApi
from src.models.entrypoints import GBIFSpeciesSearchParams
from src.log import with_logging

from src.parser import parse, GBIFPath


description = """
Search species name usages with full-text search across scientific names, vernacular names, 
descriptions, and taxonomic classifications. Results ordered by relevance.

Search examples:
• "Puma concolor" → Find specific species by scientific name
• "jaguar" → Search by common name across all languages  
• "endangered cats" → Full-text search in descriptions and classifications
• "Quercus" → Find all oak species and related taxa
• "marine mammals" → Search descriptions and habitat information
"""

entrypoint = AgentEntrypoint(
    id="search_species",
    description="Search species name usages",
    parameters=GBIFSpeciesSearchParams,
)


@with_logging("search_species")
async def run(
    context: ResponseContext, request: str, params: Optional[GBIFSpeciesSearchParams]
):
    """
    Executes the species search entrypoint. Searches for species name usages using the provided
    parameters and creates an artifact with the results.
    """
    # Generate a unique agent log ID for this run for logging purposes
    AGENT_LOG_ID = f"SEARCH_SPECIES_{str(uuid.uuid4())[:6]}"

    await context.reply("Parsing request parameters using LLM...")
    params = await parse(request, GBIFPath.SPECIES, GBIFSpeciesSearchParams)

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
            returned = len(raw_response.get('results', []))

            await process.log(f"Query successful, found {total} species records.")
            await process.create_artifact(
                mimetype="application/json",
                description=f"Raw JSON for {returned} GBIF species name usage records",
                uris=[api_url],
                metadata={
                    "data_source": "GBIF",
                    "record_count": returned,
                    "total_matches": total,
                    "search_type": "species_name_usage",
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
