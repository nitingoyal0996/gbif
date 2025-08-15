"""
GBIF Count Species Records Entrypoint

This entrypoint counts species name usage records and provides faceted statistics using the GBIF species API.
Provides statistical breakdowns of taxonomic data by various classification and status dimensions.
"""
import uuid

from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentEntrypoint

from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from src.models.entrypoints import GBIFSpeciesFacetsParams
from src.log import with_logging, logger
from src.gbif.parser import parse, GBIFPath

description = """
This entrypoint works against data kept in the GBIF Checklist Bank which taxonomically indexes all registered checklist datasets in the GBIF network. And it provides services for counting species name usage records with statistical breakdowns by taxonomic, conservation, and nomenclatural dimensions.
"""

entrypoint = AgentEntrypoint(
    id="count_species_records",
    description="Count species records with faceted statistics",
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
            f"GBIF: Request received: {request}. Generating iChatBio for GBIF request parameters..."
        )

        response = await parse(request, GBIFPath.SPECIES, GBIFSpeciesFacetsParams)
        params = response.search_parameters
        description = response.artifact_description
        await process.log(
            "GBIF: Generated search and facet parameters: ",
            data=params.model_dump(exclude_defaults=True),
        )

        api = GbifApi()
        api_url = api.build_species_facets_url(params)
        await process.log(f"GBIF: Generated API URL: {api_url}")

        try:
            await process.log(f"GBIF: Sending data retrieval request to {api_url}...")
            raw_response = await execute_request(api_url)
            status_code = raw_response.get("status_code", 200)
            if status_code != 200:
                await process.log(
                    f"GBIF: Data retrieval failed with status code {status_code}",
                    data=raw_response,
                )
                await context.reply(
                    f"Data retrieval failed with status code {status_code}",
                )
                return
            await process.log(
                f"GBIF: Data retrieval successful, status code {status_code}"
            )
            await process.log(f"GBIF: Processing response and preparing artifact...")

            total = raw_response.get("count", 0)
            facets = raw_response.get("facets", [])
            portal_url = api.build_portal_url(api_url)

            await process.create_artifact(
                mimetype="application/json",
                description=description,
                uris=[api_url],
                metadata={
                    "portal_url": portal_url,
                    "data_source": "GBIF Species",
                    "data": raw_response,
                },
            )

            summary = _generate_response_summary(total, facets, portal_url)
            await context.reply(summary)

        except Exception as e:
            await process.log(
                f"GBIF: Error during API request",
                data={
                    "error": str(e),
                    "agent_log_id": AGENT_LOG_ID,
                    "api_url": api_url,
                },
            )
            await context.reply(
                f"I encountered an error while trying to count species records: {str(e)}",
            )


def _generate_response_summary(total: int, facets: list[dict], portal_url: str) -> str:
    if total > 0:
        summary = f"I have successfully retrieved {total} species records. "
    else:
        summary = f"I have not found any species records matching your criteria. "
    if facets:
        summary += (
            f"Facet fields: {[facet.get('field', 'unknown') for facet in facets]} "
        )
    summary += f"The results can also be viewed in the GBIF portal at {portal_url}."
    return summary
