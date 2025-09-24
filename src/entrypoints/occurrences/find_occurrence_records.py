import uuid
import openai
import json

from dataclasses import dataclass
from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.entrypoints import GBIFOccurrenceSearchParams
from src.models.validators import OccurrenceSearchParamsValidator
from src.log import with_logging, logger
from src.gbif.parser import parse
from src.gbif.resolve_parameters import (
    resolve_names_to_taxonkeys,
    resolve_pending_search_parameters,
)
import dataclasses


description = """
**Use Case:** Use this entrypoint to search for and retrieve a list of individual occurrence records that match specific filters. This is the primary tool for fetching raw data.

**Triggers On:** User requests that may ask to "find," "list," or "show records of" something. It's for when the user wants to see the actual data entries, not a summary of them. It may also ask for records of a specific species, location, or time period.

**Key Inputs:** Requires specific search criteria like scientificName, taxonKey, country, year, or geographic coordinates (latitude, longitude).

**Limitations:** This entrypoint does not perform summaries or counts. It also does not sort the results.
"""

entrypoint = AgentEntrypoint(
    id="find_occurrence_records",
    description=description,
    parameters=None,
)


def serialize_for_log(obj):
    # Pydantic v2
    if hasattr(obj, "model_dump"):
        return obj.model_dump(exclude_defaults=True)
    # Dataclass
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    # Fallback
    return str(obj)


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
            f"Request recieved: {request} \n\nGenerating iChatBio for GBIF request parameters..."
        )

        response = await parse(request, entrypoint.id, OccurrenceSearchParamsValidator)
        logger.info(f"Parsed Response: {response}")
        api = GbifApi()

        param_result = await _get_parameters(response, request, api, process)

        if param_result.clarification_needed:
            await context.reply(param_result.clarification_message)
            return

        logger.info(
            f"Search parameters: {serialize_for_log(param_result.search_params)}"
        )

        api_url = api.build_occurrence_search_url(param_result.search_params)
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
                f"I encountered an error while trying to search for occurrences: {str(e)}",
            )


def _generate_response_summary(page_info: dict, portal_url: str) -> str:
    if page_info.get("count") > 0:
        summary = f"I have successfully searched for occurrences and matching records. Retreived {page_info.get('limit')} records per page, {page_info.get('offset')} records offset. Total records found: {page_info.get('count')}. "
    else:
        summary = "I have not found any occurrence records matching your criteria. "
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary


@dataclass
class ParameterResolutionResult:
    search_params: GBIFOccurrenceSearchParams
    clarification_needed: bool
    clarification_message: str = None


async def _get_parameters(
    response: GBIFOccurrenceSearchParams,
    request: str,
    api: GbifApi,
    process: IChatBioAgentProcess,
) -> ParameterResolutionResult:
    """
    Executes the occurrence search entrypoint. Searches for occurrence records using the provided
    parameters and creates an artifact with the results.
    """
    resolved_fields = {}
    unresolved_fields = []
    clarification_message = None
    clarification_needed = response.clarification_needed

    # Collect all updates first, then do a single copy operation
    params_updates = {}

    if response.clarification_needed:
        resolved_fields, unresolved_fields = await resolve_pending_search_parameters(
            response.unresolved_params or [], request, api, process
        )
        if resolved_fields:
            params_updates.update(resolved_fields)
        if unresolved_fields:
            # Create params with current updates for the early return case
            clarification_message = await _generate_resolution_message(
                request,
                response,
                resolved_fields,
                unresolved_fields,
            )
            return ParameterResolutionResult(
                search_params=None,
                clarification_needed=True,
                clarification_message=clarification_message,
            )
        else:
            clarification_needed = False

    # Check if we need to resolve scientific names (before creating the final params)
    base_params = response.params.model_copy(update=params_updates)
    if getattr(base_params, "scientificName", None):
        await process.log(
            f"Resolving {base_params.scientificName} scientific names to taxon keys for better search results..."
        )
        taxon_keys = await resolve_names_to_taxonkeys(
            api, base_params.scientificName, process
        )
        if taxon_keys:
            params_updates.update(
                {
                    "taxonKey": [int(key) for key in taxon_keys],
                    "scientificName": None,
                }
            )
        else:
            await process.log(
                "Failed to resolve any scientific names to taxon keys, using original parameters"
            )

    # Single copy operation with all updates
    params = response.params.model_copy(update=params_updates)

    return ParameterResolutionResult(
        search_params=params,
        clarification_needed=clarification_needed,
        clarification_message=clarification_message,
    )


async def _generate_resolution_message(
    user_request: str,
    response: GBIFOccurrenceSearchParams,
    resolved_fields: dict,
    unresolved_fields: list,
) -> str:
    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that crafts a brief message (don't make it an email) to clarify the search parameters. Include what were we able to resolve and what we still need to clarify.",
            },
            {
                "role": "user",
                "content": f"Generate the message for:\nUser request: {user_request}\nParsed Response: {json.dumps(response.model_dump(exclude_defaults=True))}\nResolved fields: {resolved_fields}\nUnresolved fields: {unresolved_fields}.",
            },
        ]
        client = openai.AsyncOpenAI()
        response = await client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            max_tokens=200,
        )
        message_content = response.choices[0].message.content
        return message_content

    except Exception as e:
        logger.error(
            f"LLM extraction failed, falling back to default message: {str(e)}"
        )
        return "I encountered an error while trying to generate a message about the clarification required from the user about their search."
