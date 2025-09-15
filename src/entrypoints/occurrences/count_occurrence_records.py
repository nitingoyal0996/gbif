import uuid

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.entrypoints import GBIFOccurrenceFacetsParams
from src.models.validators import OccurrenceFacetsParamsValidator
from src.log import with_logging

from src.gbif.parser import parse
from src.gbif.resolve_parameters import resolve_names_to_taxonkeys


description = """
**Use Case:** Use this entrypoint to get statistical summaries, counts, and breakdowns of occurrence data using facets. This is the tool for aggregation, not for fetching individual records.

**Triggers On:** User requests that may ask "how many," for a "count of," a "breakdown by," a "summary of," or the "distribution of" records.

**Key Inputs:** Requires one or more facet fields (e.g., country, year, basisOfRecord) to group the data. Can be combined with search filters like scientificName.

**Limitations:** This entrypoint returns aggregated counts, not a list of individual records.
"""


entrypoint = AgentEntrypoint(
    id="count_occurrence_records",
    description=description,
    parameters=None,
)


@with_logging("count_occurrence_records")
async def run(context: ResponseContext, request: str):
    """
    Executes the occurrence counting entrypoint. Counts occurrence records using the provided
    parameters and creates an artifact with the faceted results.
    """

    async with context.begin_process("Requesting GBIF statistics") as process:
        AGENT_LOG_ID = f"COUNT_OCCURRENCE_RECORDS_{str(uuid.uuid4())[:6]}"
        await process.log(
            f"Request recieved: {request}. Generating iChatBio for GBIF request parameters..."
        )
        response = await parse(request, entrypoint.id, OccurrenceFacetsParamsValidator)
        if response.clarification_needed:
            await process.log("Stopping execution to clarify the request")
            await context.reply(f"{response.clarification_reason}")
            return

        params = response.search_parameters
        description = response.artifact_description
        await process.log(
            "Generated search and facet parameters: ",
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
                    "Failed to resolve any scientific names to taxon keys, using original parameters."
                )

        api_url = api.build_occurrence_facets_url(search_params)
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
                    f"Data retrieval failed with status code {status_code}"
                )
                return
            await process.log(f"Data retrieval successful, status code {status_code}")
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
                    "data_source": "GBIF Occurrence",
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
                f"I encountered an error while trying to count occurrences: {str(e)}",
            )


def _generate_response_summary(page_info: dict, portal_url: str) -> str:
    if page_info.get("count") > 0:
        summary = f"I have found {page_info.get('count')} occurrence records matching your criteria. "
    else:
        summary = "I have not found any occurrence records matching your criteria. "
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary


async def _update_search_params(
    params: GBIFOccurrenceFacetsParams,
    taxon_keys: list,
    process: IChatBioAgentProcess,
) -> GBIFOccurrenceFacetsParams:
    taxon_key_ints = [int(key) for key in taxon_keys]
    search_params_data = params.model_dump(exclude_defaults=True)
    search_params_data["taxonKey"] = taxon_key_ints
    search_params_data["scientificName"] = None
    search_params = GBIFOccurrenceFacetsParams(**search_params_data)
    await process.log(
        f"Created new search parameters with taxon keys: {taxon_key_ints} and preserved other parameters"
    )
    return search_params
