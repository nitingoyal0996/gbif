"""
GBIF Count Species Records Entrypoint

This entrypoint counts species name usage records and provides faceted statistics using the GBIF species API.
Provides statistical breakdowns of taxonomic data by various classification and status dimensions.
"""
import uuid

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.api import GbifApi
from src.models.entrypoints import GBIFSpeciesFacetsParams
from src.log import with_logging


description = """
Count and analyze species name usage records with statistical breakdowns by taxonomic, conservation, and nomenclatural dimensions.

Examples of what you can discover:
• "How many species are in each taxonomic rank?" → facet=["rank"] 
• "What's the conservation status breakdown for mammals?" → q="mammalia", facet=["threat"]
• "Which datasets contribute the most marine species?" → habitat="MARINE", facet=["datasetKey"]
• "Compare taxonomic vs nomenclatural status distributions" → facet=["status", "nomenclaturalStatus"]
• "How many accepted vs synonym names by rank?" → facet=["rank", "status"]

Common facet dimensions:
- rank: Species, genus, family, order, etc.
- status: Accepted, synonym, doubtful names
- habitat: Marine, freshwater, terrestrial
- threat: IUCN conservation status categories
- nameType: Scientific, hybrid, cultivar names
- datasetKey: Contributing taxonomic datasets
"""

entrypoint = AgentEntrypoint(
    id="count_species_records",
    description="Count species records with faceted statistics",
    parameters=GBIFSpeciesFacetsParams
)


@with_logging("count_species_records")
async def run(
    context: ResponseContext, request: str, params: GBIFSpeciesFacetsParams
):
    """
    Executes the species counting entrypoint. Counts species name usage records using the provided
    parameters and creates an artifact with the faceted statistical results.
    """
    # Generate a unique agent log ID for this run for logging purposes
    AGENT_LOG_ID = f"COUNT_SPECIES_RECORDS_{str(uuid.uuid4())[:6]}"

    async with context.begin_process("Counting GBIF species records with facets") as process:
        process: IChatBioAgentProcess
        await process.log(f"Agent log ID: {AGENT_LOG_ID}")
        await process.log(
            "Search and facet parameters", data=params.model_dump(exclude_defaults=True)
        )

        gbif_api = GbifApi()
        api_url = gbif_api.build_species_facets_url(params)
        await process.log(f"Constructed API URL: {api_url}")

        try:
            await process.log("Querying GBIF for species statistics...")
            raw_response = await gbif_api.execute_request(api_url)

            total = raw_response.get('count', 0)
            facets = raw_response.get('facets', [])

            await process.log(
                f"Query successful, found {total} species records with {len(facets)} facet groups."
            )
            await process.create_artifact(
                mimetype="application/json",
                description=f"Raw JSON for GBIF species statistics with {len(facets)} facet groups",
                uris=[api_url],
                metadata={
                    "data_source": "GBIF",
                    "total_matches": total,
                    "facet_groups": len(facets),
                    "facet_fields": [facet.get("field", "unknown") for facet in facets],
                    "search_type": "species_facets",
                    "portal_url": gbif_api.build_portal_url(api_url),
                },
            )

            summary = f"I have successfully counted species records and found {total} matching name usage records. "
            if facets:
                facet_summary = ", ".join([f"{facet.get('field', 'unknown')} ({len(facet.get('counts', []))} values)" for facet in facets])
                summary += f"The results are broken down by: {facet_summary}. "
            summary += f"The statistical breakdown can be viewed in the GBIF portal at {gbif_api.build_portal_url(api_url)}."

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
            await context.reply(f"I encountered an error while trying to count species records: {str(e)}") 