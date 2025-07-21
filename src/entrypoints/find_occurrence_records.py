"""
GBIF Find Occurrence Records Entrypoint

This entrypoint searches for species occurrence records using the GBIF occurrences API.
Parameters are provided by the upstream service - no LLM generation needed.
"""

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.api import GbifApi
from src.models.entrypoints import GBIFOccurrenceSearchParams


description = """
Searches for species occurrence records using the GBIF occurrences API. Returns the total number
of records found, the URL constructed to query the GBIF occurrences API, and a URL to view
the results on the GBIF web portal.

Parameters include search criteria such as:
- Scientific names, common names, or full-text search
- Geographic filters (country, continent, coordinates)
- Temporal filters (year, month, date ranges)
- Taxonomic filters (kingdom, phylum, class, etc.)
- Record type filters (basis of record, occurrence status)
- Pagination parameters (limit, offset)
"""

entrypoint = AgentEntrypoint(
    id="find_occurrence_records",
    description="Find occurrence records",
    parameters=GBIFOccurrenceSearchParams
)


async def run(context: ResponseContext, request: str, params: GBIFOccurrenceSearchParams):
    """
    Executes the occurrence search entrypoint. Searches for occurrence records using the provided
    parameters and creates an artifact with the results.
    """
    async with context.begin_process("Searching GBIF occurrence records") as process:
        process: IChatBioAgentProcess
        
        gbif_api = GbifApi()
        
        await process.log("Extracted search parameters", data=params.model_dump(exclude_defaults=True))
        
        # Build the API URL
        api_url = gbif_api.build_occurrence_search_url(params)
        await process.log(f"Constructed API URL: {api_url}")
        
        try:
            await process.log("Querying GBIF for occurrence data...")
            raw_response = await gbif_api.execute_request(api_url)
            
            total = raw_response.get('count', 0)
            returned = len(raw_response.get('results', []))
            
            await process.log(f"Query successful, found {total} records.")
            
            # Create artifact with the results
            await process.create_artifact(
                mimetype="application/json",
                description=f"Raw JSON for {returned} GBIF occurrence records",
                uris=[api_url],
                metadata={
                    "data_source": "GBIF",
                    "record_count": returned,
                    "total_matches": total,
                    "portal_url": gbif_api.build_portal_url(api_url)
                }
            )
            
            # Reply to the assistant with a summary
            summary = f"I have successfully searched for occurrences and found {total} matching records. "
            if returned < total:
                summary += f"I've returned {returned} records in this response. "
            summary += f"The results can be viewed in the GBIF portal at {gbif_api.build_portal_url(api_url)}."
            
            await context.reply(summary)
            
        except Exception as e:
            await process.log("Error during API request", data={"error": str(e)})
            await context.reply(f"I encountered an error while trying to search for occurrences: {str(e)}")
