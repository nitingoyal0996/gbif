import uuid

from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.validators import SpeciesFacetsParamsValidator
from src.log import with_logging, logger
from src.gbif.parser import parse

description = """
**Use Case:** Use this entrypoint to get statistical counts and summaries of species themselves, based on criteria like taxonomic rank, conservation status, or habitat.

**Triggers On:** User requests asking "how many species," for a "count of species," a "breakdown of species by," or "statistics on" taxonomic groups.

**Key Inputs:** One or more facet fields (e.g., rank, status, habitat).

**Key Outputs:** Aggregated counts of species, not individual species data or their occurrences.

**Crucial Distinction:** This is for counting taxonomic entities (e.g., "how many species of birds are endangered?"), not their real-world observations.

Limitations: This entrypoint does not support searching species with location information. Occurrence API should be used instead.
"""

entrypoint = AgentEntrypoint(
    id="count_species_records",
    description=description,
    parameters=None,
)


@with_logging("count_species_records")
async def run(context: ResponseContext, request: str):
    """
    Executes the species counting entrypoint. Counts species name usage records using the provided
    parameters and creates an artifact with the faceted statistical results.
    """
    async with context.begin_process("Requesting GBIF statistics") as process:
        AGENT_LOG_ID = f"COUNT_SPECIES_RECORDS_{str(uuid.uuid4())[:6]}"
        await process.log(
            f"Request received: {request} \n\nGenerating iChatBio for GBIF request parameters..."
        )

        response = await parse(request, entrypoint.id, SpeciesFacetsParamsValidator)
        if response.clarification_needed:
            await process.log(f"Clarification needed: {response.clarification_reason}")
            await context.reply(f"{response.clarification_reason}")
            return
        logger.info(f"LLM Parsed Response: {response}")
        params = response.params
        description = response.artifact_description

        await process.log(
            "Generated search and facet parameters: ",
            data=params.model_dump(exclude_defaults=True),
        )
        api = GbifApi()
        api_url = api.build_species_facets_url(params)
        await process.log(f"Generated API URL: {api_url}")

        try:
            await process.log(f"Sending data retrieval request to {api_url}...")
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
            # create a log of some informative fields from the response about the record
            page_info = {
                "count": raw_response.get("count"),
                "limit": raw_response.get("limit"),
                "offset": raw_response.get("offset"),
            }
            await process.log(
                "API pagination information of the response: ", data=page_info
            )
            await process.log("Processing response and preparing artifact...")

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
                f"I encountered an error while trying to count species records: {str(e)}",
            )


def _generate_response_summary(page_info: dict, portal_url: str) -> str:
    if page_info.get("count") > 0:
        summary = f"I have found {page_info.get('count')} species records matching your criteria. "
    else:
        summary = "I have not found any species records matching your criteria. "
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary
