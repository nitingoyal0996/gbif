import uuid

from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.entrypoints import GBIFDatasetSearchParams
from src.log import with_logging, logger
from src.gbif.parser import parse, GBIFPath


description = """
This entrypoint works against the GBIF Registry, which handles dataset metadata. This entrypoint provides services for full-text search across all datasets with comprehensive filtering options.

The GBIF Registry includes various types of data sources:
- Datasets: The primary data containers that can include occurrences, checklists, metadata, or sampling events
- Recordsets: Often synonymous with datasets, representing organized collections of data records
- Collections: Primarily specimen-based datasets, though some collections may include observation records

Important distinctions:
- Occurrence datasets may contain specimen collections, observation records, or both
- Observation records (occurrences without collected specimens) are not part of specimen collections
- Checklist datasets focus on taxonomic information rather than individual occurrences
- Metadata datasets provide descriptive information about other datasets

Results are ordered by relevance and can be filtered by dataset type, organization, geographic coverage, temporal coverage, license, and many other criteria. Faceting is also supported for analyzing result distributions.
"""

entrypoint = AgentEntrypoint(
    id="find_datasets",
    description=description,
    parameters=None,
)


@with_logging("find_datasets")
async def run(context: ResponseContext, request: str):
    """
    Executes the dataset search entrypoint. Searches for datasets using the provided
    parameters and creates an artifact with the results.
    """
    async with context.begin_process("Requesting GBIF Dataset Search") as process:
        AGENT_LOG_ID = f"FIND_DATASETS_{str(uuid.uuid4())[:6]}"
        logger.info(f"Agent log ID: {AGENT_LOG_ID}")
        await process.log(
            f"Request received: {request}. Generating iChatBio for GBIF request parameters..."
        )

        response = await parse(request, GBIFPath.REGISTRY, GBIFDatasetSearchParams)
        params = response.search_parameters
        description = response.artifact_description
        await process.log(
            "Generated search parameters",
            data=params.model_dump(exclude_defaults=True),
        )

        api = GbifApi()

        api_url = api.build_dataset_search_url(params)
        await process.log(f"Constructed API URL: {api_url}")

        try:
            await process.log("Querying GBIF for dataset data...")
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

            total = raw_response.get("count", 0)
            portal_url = api.build_portal_url(api_url)

            await process.create_artifact(
                mimetype="application/json",
                description=description,
                uris=[api_url],
                metadata={
                    "portal_url": portal_url,
                    "data_source": "GBIF Registry",
                },
            )

            summary = _generate_response_summary(total, portal_url)
            await context.reply(summary)

        except Exception as e:
            await process.log(
                f"Error during API request",
                data={
                    "error": str(e),
                    "agent_log_id": AGENT_LOG_ID,
                    "api_url": api_url,
                },
            )
            await context.reply(
                f"I encountered an error while trying to search for datasets: {str(e)}",
            )


def _generate_response_summary(total: int, portal_url: str) -> str:
    if total > 0:
        summary = (
            f"I have successfully searched for datasets and found matching records. "
        )
    else:
        summary = f"I have not found any datasets matching your criteria. "
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary
