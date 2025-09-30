import uuid
import instructor
import json

from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import Optional
from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.entrypoints import GBIFOccurrenceFacetsParams
from src.models.validators import OccurrenceFacetsParamsValidator
from src.log import with_logging, logger

from src.gbif.parser import parse
from src.gbif.resolve_parameters import (
    resolve_names_to_taxonkeys,
    resolve_pending_search_parameters,
    resolvable_fields,
    resolve_keys_to_names,
)
import dataclasses


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


def serialize_for_log(obj):
    # Pydantic v2
    if hasattr(obj, "model_dump"):
        return obj.model_dump(exclude_defaults=True)
    # Dataclass
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    # Fallback
    return str(obj)


@dataclass
class ParameterResolutionResult:
    search_params: Optional[GBIFOccurrenceFacetsParams]
    clarification_needed: bool
    clarification_message: str = None


@with_logging("count_occurrence_records")
async def run(context: ResponseContext, request: str):
    """
    Executes the occurrence counting entrypoint. Counts occurrence records using the provided
    parameters and creates an artifact with the faceted results.
    """

    async with context.begin_process("Requesting GBIF statistics") as process:
        AGENT_LOG_ID = f"COUNT_OCCURRENCE_RECORDS_{str(uuid.uuid4())[:6]}"
        logger.info(f"Agent log ID: {AGENT_LOG_ID}")
        await process.log(f"Request recieved: {request} \n\nParsing request...")

        response = await parse(request, entrypoint.id, OccurrenceFacetsParamsValidator)
        logger.info(f"Parsed Response: {response}")
        api = GbifApi()

        param_result = await _get_parameters(response, request, api, process)

        await process.log(
            f"Search API parameters results -", data=serialize_for_log(param_result)
        )

        if param_result.clarification_needed:
            await context.reply(param_result.clarification_message)
            return

        search_params = param_result.search_params

        api_url = api.build_occurrence_facets_url(search_params)

        try:
            await process.log(f"Sending data retrieval request to GBIF -", data={"url": api_url})
            raw_response = await execute_request(api_url)
            status_code = raw_response.get("status_code", 200)
            if status_code != 200:
                await process.log(
                    f"Data retrieval failed with status code {status_code} -",
                    data=raw_response,
                )
                await context.reply(
                    f"Data retrieval failed with status code {status_code}"
                )
                return
            await process.log(f"Data retrieval successful, status code {status_code}")

            await process.log("Resolving facet keys to scientific names if applicable")
            facets = raw_response.get("facets", [])
            enriched_facets = await _enrich_facets_with_names(api, process, facets)
            raw_response["facets"] = enriched_facets

            page_info = {
                "count": raw_response.get("count"),
                "facetLimit": search_params.facetLimit,
                "facetOffset": search_params.facetOffset,
            }
            await process.log(
                "API pagination information of the response -", data=page_info
            )

            portal_url = api.build_portal_url(api_url)

            artifact_description = await _generate_artifact_description(
                json.dumps(search_params.model_dump(exclude_none=True))
            )
            content_bytes = json.dumps(raw_response, indent=2).encode("utf-8")
            await process.create_artifact(
                mimetype="application/json",
                description=artifact_description,
                uris=[api_url],
                content=content_bytes,
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


async def _get_parameters(
    response: GBIFOccurrenceFacetsParams,
    request: str,
    api: GbifApi,
    process: IChatBioAgentProcess,
) -> ParameterResolutionResult:
    """
    Executes the occurrence facets entrypoint. Counts occurrence records using the provided
    parameters and creates an artifact with the faceted results.
    """
    resolved_fields = {}
    unresolved_fields = []
    clarification_message = None
    clarification_needed = response.clarification_needed

    # Collect all updates first, then do a single copy operation
    params_updates = {}

    if response.clarification_needed:
        await process.log(
            f"{response.clarification_reason} -",
            data={"unresolved_params": response.unresolved_params},
        )
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
            await process.log(f"Request parsed successfully...")
            clarification_needed = False

    # Check if we need to resolve scientific names (before creating the final params)
    base_params = response.params.model_copy(update=params_updates)
    if getattr(base_params, "scientificName", None):
        await process.log(
            f"Resolving {base_params.scientificName} scientific names to taxon keys..."
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
    response: OccurrenceFacetsParamsValidator,
    resolved_fields: dict,
    unresolved_fields: list,
) -> str:

    class ResolutionMessage(BaseModel):
        message: str = Field(
            ...,
            description="a brief message to clarify the search parameters",
        )

    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that crafts a brief message (don't make it an email) to clarify the search parameters. Include what were you able to resolve and what you still need to clarify.",
            },
            {
                "role": "user",
                "content": f"Generate the message for:\nUser request: {user_request}\nParsed Response: {json.dumps(serialize_for_log(response))}\nResolved fields: {resolved_fields}\nUnresolved fields: {unresolved_fields}.",
            },
        ]
        client = instructor.from_provider(
            "openai/gpt-4.1-nano",
            async_client=True,
        )
        response = await client.chat.completions.create(
            messages=messages,
            response_model=ResolutionMessage,
            max_tokens=100,
        )
        message_content = response.message
        return message_content

    except Exception as e:
        logger.error(
            f"LLM extraction failed, falling back to default message: {str(e)}"
        )
        return "I encountered an error while trying to generate a message about the clarification required from the user about their search."


async def _generate_artifact_description(search_parameters: str) -> str:

    class ArtifactDescription(BaseModel):
        description: Optional[str] = Field(
            description="A concise characterization of the retrieved record statistics.",
            examples=[
                "Per-country record counts for species Rattus rattus",
                "Per-species record counts for records created in 2025",
            ],
            default=None,
        )

    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that crafts a brief yet meaningful description of the artifact based on request parameters.",
            },
            {
                "role": "user",
                "content": f"Generate description for request: \nParameters: {search_parameters}",
            },
        ]
        client = instructor.from_provider(
            model="openai/gpt-4.1-nano",
            async_client=True,
        )
        response = await client.chat.completions.create(
            messages=messages,
            response_model=ArtifactDescription,
            max_tokens=50,
        )
        message_content = response.description
        return message_content
    except Exception as e:
        logger.error(
            f"LLM extraction failed, falling back to default description: {str(e)}"
        )
        return "I encountered an error while trying to generate a description of the artifact."


async def _enrich_facets_with_names(
    api: GbifApi, process: IChatBioAgentProcess, facets: list
) -> list:
    """
    Enrich facet results by adding scientific names for taxonomic key facets.
    """
    taxonomic_facet_fields = {
        "SPECIES_KEY",
        "GENUS_KEY",
        "FAMILY_KEY",
        "ORDER_KEY",
        "CLASS_KEY",
        "PHYLUM_KEY",
        "KINGDOM_KEY",
        "TAXON_KEY",
    }

    enriched_facets = []

    for facet in facets:
        field = facet.get("field", "")
        if field in taxonomic_facet_fields:
            counts = facet.get("counts", [])
            keys = [int(count.get("name")) for count in counts if count.get("name")]

            if keys:
                key_to_name = await resolve_keys_to_names(api, process, keys, field)
                enriched_counts = []
                for count in counts:
                    key = count.get("name")
                    if key and int(key) in key_to_name:
                        enriched_count = count.copy()
                        enriched_count["scientificName"] = key_to_name[int(key)]
                        enriched_counts.append(enriched_count)
                    else:
                        enriched_counts.append(count)
                enriched_facet = facet.copy()
                enriched_facet["counts"] = enriched_counts
                enriched_facets.append(enriched_facet)
            else:
                enriched_facets.append(facet)
        else:
            enriched_facets.append(facet)
    return enriched_facets
