import uuid
import json

from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.validators import SpeciesFacetsParamsValidator
from src.log import with_logging, logger
from src.gbif.parser import parse
from src.utils import _preprocess_user_request, serialize_organisms
from src.gadm.gadm import map_locations_to_gadm, serialize_locations

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
    async with context.begin_process("Requesting GBIF Species statistics") as process:
        AGENT_LOG_ID = f"COUNT_SPECIES_RECORDS_{str(uuid.uuid4())[:6]}"
        await process.log(f"Request received: {request} \n\nParsing request...")

        expansion_response = await _preprocess_user_request(request)
        enrich_locations = await map_locations_to_gadm(expansion_response.locations)
        expandedRequest = f"User request: {request} Identified organisms in the request: {json.dumps(serialize_organisms(expansion_response.organisms))} Identified locations in the request: {json.dumps(serialize_locations(enrich_locations))}"
        await process.log(
            f"Expanded request",
            data={
                "original_request": request,
                "identified_organisms": serialize_organisms(
                    expansion_response.organisms
                ),
                "identified_locations": serialize_locations(enrich_locations),
            },
        )

        response = await parse(
            expandedRequest,
            entrypoint.id,
            SpeciesFacetsParamsValidator,
            expansion_response,
        )
        logger.info(f"Parameter parsing plan: {response}")
        await process.log(f"Parameter parsing plan", data={"plan": response.plan})
        if response.clarification_needed:
            await process.log(
                f"Clarification needed",
                data={"clarification_reason": response.clarification_reason},
            )
            await context.reply(f"{response.clarification_reason}")
            return

        await process.log(
            f"Final Search Parameters",
            data=response.params.model_dump(exclude_none=True),
        )
        params = response.params
        description = response.artifact_description

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
                "facetLimit": params.facetLimit,
                "facetOffset": params.facetOffset,
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
                f"I encountered an error while trying to count species records: {str(e)}",
            )


def _generate_response_summary(page_info: dict, portal_url: str) -> str:
    if page_info.get("count") > 0:
        summary = f"I have found {page_info.get('count')} species records matching your criteria. "
    else:
        summary = "I have not found any species records matching your criteria. "
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary
