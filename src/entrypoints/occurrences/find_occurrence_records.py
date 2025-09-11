import uuid
from pydantic import BaseModel, model_validator, ValidationInfo

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.entrypoints import GBIFOccurrenceSearchParams
from src.log import with_logging, logger
from src.gbif.parser import parse, GBIFPath
from src.gbif.resolve_parameters import resolve_names_to_taxonkeys


description = """
**Use Case:** Use this entrypoint to search for and retrieve a list of individual occurrence records that match specific filters. This is the primary tool for fetching raw data.

**Triggers On:** User requests that may ask to "find," "list," or "show records of" something. It's for when the user wants to see the actual data entries, not a summary of them. It may also ask for records of a specific species, location, or time period.

**Key Inputs:** Requires specific search criteria like scientificName, taxonKey, country, year, or geographic coordinates (latitude, longitude).

**Limitations:** This entrypoint does not perform summaries or counts. It also does not sort the results.
"""

fewshot = [
    {
        "user_request": "Find occurrences of jaguars",
        "search_parameters": None,
        "clarification_needed": True,
        "clarification_reason": "I need either scientificName or taxonKey to search for occurrences.",
    },
    {
        "user_request": "Find occurrences of Panthera onca in the US",
        "search_parameters": {"scientificName": "Panthera onca", "country": "US"},
        "clarification_needed": False,
        "clarification_reason": None,
    },
    {
        "user_request": "Find occurrences of Panthera onca in the Plam Spring, CA in 2020",
        "search_parameters": None,
        "clarification_needed": True,
        "clarification_reason": "I need latitude and longitude of Plam Spring, CA to search for occurrences.",
    },
]


# mixin for validation
class InstructorValidationMixin(BaseModel):
    @model_validator(mode="after")
    def validate_values_are_from_request(self, info: ValidationInfo):
        user_request = info.context.get("user_request")
        if not user_request:
            return self

        # Explicitly check for latitude, longitude, and all keys/IDs
        key_fields = [
            "decimalLatitude",
            "decimalLongitude",
            "taxonKey",
            "datasetKey",
            "kingdomKey",
            "phylumKey",
            "classKey",
            "orderKey",
            "familyKey",
            "speciesKey",
            "genusKey",
            "occurrenceId",
            "eventId",
            "recordNumber",
            "collectionCode",
            "institutionCode",
            "catalogNumber",
        ]
        # throw error if there is no value
        if not any(self.model_dump().values()):
            raise ValueError("No values provided for any parameter")
        for field, value in self.model_dump().items():
            if value is None:
                continue
            if field in key_fields:
                values_to_check = value if isinstance(value, list) else [value]
                for v in values_to_check:
                    if str(v).lower() not in user_request.lower():
                        if field in ["decimalLatitude", "decimalLongitude"]:
                            raise ValueError(
                                f"The value '{v}' for field '{field}' (latitude/longitude) was not found in the original request. "
                                "You must provide explicit latitude and longitude values; they cannot be inferred or made up."
                            )
                        else:
                            raise ValueError(
                                f"The value '{v}' for field '{field}' (key or ID) was not found in the original request. "
                                "You must provide explicit keys or IDs; they cannot be inferred or made up."
                            )
        return self


class OccurrenceSearchParams(InstructorValidationMixin, GBIFOccurrenceSearchParams):
    pass


entrypoint = AgentEntrypoint(
    id="find_occurrence_records",
    description=description,
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

        response = await parse(request, entrypoint.id, OccurrenceSearchParams, fewshot)

        if response.clarification_needed:
            await process.log("Stopping execution to clarify the request")
            await context.reply(f"{response.clarification_reason}")
            return

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

        logger.info(f"Search parameters: {search_params}")

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
