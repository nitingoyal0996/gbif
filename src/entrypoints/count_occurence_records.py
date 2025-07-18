"""
GBIF Count Occurrence Records Entrypoint

This entrypoint counts occurrence records and provides faceted statistics using the GBIF occurrences API.
Parameters are provided by the upstream service - no LLM generation needed.
"""

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from gbif_logic import GBIF
from models.entrypoints import GBIFOccurrenceFacetsParams


description = """
Counts occurrence records and provides faceted statistics using the GBIF occurrences API. Returns the total
number of records found, breakdown by specified facets, the URL constructed to query the GBIF occurrences API,
and a URL to view the results on the GBIF web portal.

Parameters are provided by the upstream service and include search criteria plus facet specifications:
- Search filters (same as find_occurrence_records)
- Facet fields to analyze (scientificName, country, year, etc.)
- Facet minimum count thresholds
- Facet selection options
"""

entrypoint = AgentEntrypoint(
    id="count_occurrence_records",
    description="Count occurrence records with facets",
    parameters=GBIFOccurrenceFacetsParams
)


async def run(context: ResponseContext, request: str, params: GBIFOccurrenceFacetsParams):
    """
    Executes the occurrence counting entrypoint. Counts occurrence records using the provided
    parameters and creates an artifact with the faceted results.
    """
    async with context.begin_process("Counting GBIF occurrence records with facets") as process:
        process: IChatBioAgentProcess
        
        gbif = GBIF()
        
        await process.log("Extracted search and facet parameters", data=params.model_dump(exclude_defaults=True))
        
        # Build the API URL
        api_url = gbif.build_occurrence_facets_url(params)
        await process.log(f"Constructed API URL: {api_url}")
        
        try:
            await process.log("Querying GBIF for occurrence statistics...")
            raw_response = await gbif.execute_request(api_url)
            
            total = raw_response.get('count', 0)
            facets = raw_response.get('facets', [])
            
            await process.log(f"Query successful, found {total} records with {len(facets)} facet groups.")
            
            # Create artifact with the results
            await process.create_artifact(
                mimetype="application/json",
                description=f"Raw JSON for GBIF occurrence statistics with {len(facets)} facet groups",
                uris=[api_url],
                metadata={
                    "data_source": "GBIF",
                    "total_matches": total,
                    "facet_groups": len(facets),
                    "facet_fields": [facet.get('field', 'unknown') for facet in facets],
                    "portal_url": gbif.build_portal_url(api_url)
                }
            )
            
            # Reply to the assistant with a summary
            summary = f"I have successfully counted occurrences and found {total} matching records. "
            if facets:
                facet_summary = ", ".join([f"{facet.get('field', 'unknown')} ({len(facet.get('counts', []))} values)" for facet in facets])
                summary += f"The results are broken down by: {facet_summary}. "
            summary += f"The results can be viewed in the GBIF portal at {gbif.build_portal_url(api_url)}."
            
            await context.reply(summary)
            
        except Exception as e:
            await process.log("Error during API request", data={"error": str(e)})
            await context.reply(f"I encountered an error while trying to count occurrences: {str(e)}")
