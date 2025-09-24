import uuid

from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.validators import SpeciesSearchParamsValidator
from src.log import with_logging, logger
from src.gbif.parser import parse


description = """
**Use Case:** Use this entrypoint to find species using a general search term (like a common or scientific name).

**Triggers On:** User requests to "search for a species," "look up," a specific organism.

**Key Inputs:** A general query string (q). This can be made more precise by using qField to target either a SCIENTIFIC_NAME or a VERNACULAR_NAME (common name). Also accepts optional filters like rank or threat status.

**Key Outputs:** A list of potential matching species, each with its essential usageKey (the taxonKey).

**Crucial Distinction:** This tool finds potential matches from a name; it does not retrieve detailed hierarchies or count occurrences.

Limitations: It cannot do searches for specific identifiers such as taxonKey, kingdomKey, etc Use taxonomic information entrypoint for that.
"""

entrypoint = AgentEntrypoint(
    id="find_species_records",
    description=description,
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
            f"Request received: {request} \n\nGenerating iChatBio for GBIF request parameters..."
        )

        response = await parse(request, entrypoint.id, SpeciesSearchParamsValidator)
        if response.clarification_needed:
            await process.log(f"Clarification needed: {response.clarification_reason}")
            await context.reply(f"{response.clarification_reason}")
            return
        logger.info(f"LLM Parsed Response: {response}")
        params = response.params
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

            page_info = {
                "count": raw_response.get("count"),
                "limit": raw_response.get("limit"),
                "offset": raw_response.get("offset"),
            }
            await process.log(
                "API pagination information of the response: ", data=page_info
            )
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

            summary = _generate_response_summary(page_info, portal_url)
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


def _generate_response_summary(page_info: dict, portal_url: str) -> str:
    if page_info.get("count") > 0:
        summary = f"I have found {page_info.get('count')} species records matching your criteria. "
    else:
        summary = "I have not found any species records matching your criteria. "
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary
