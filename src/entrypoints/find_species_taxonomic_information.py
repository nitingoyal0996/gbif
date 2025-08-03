"""
GBIF Species Taxonomic Information Entrypoint

This entrypoint retrieves comprehensive taxonomic information for a specific species
using its GBIF usage key. Provides detailed taxonomic classification, synonyms,
children taxa, and species profiles.
"""
from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.api import GbifApi
from src.models.entrypoints import GBIFSpeciesTaxonomicParams
from src.models.responses.species import NameUsage, PagingResponseNameUsage
from src.log import with_logging
from src.parser import parse, GBIFPath


entrypoint = AgentEntrypoint(
    id="species_taxonomic_information",
    name="Species Taxonomic Information",
    description="Retrieve comprehensive taxonomic information for a species using its GBIF usage key",
    examples=[
        "Get taxonomic information for species with usage key 5231190",
        "Show taxonomic hierarchy and synonyms for species 2476674",
        "Retrieve taxonomic data for species key 2877951 including children taxa"
    ]
)


@with_logging("species_taxonomic_information")
async def run(context: ResponseContext, request: str):

    async with context.begin_process("Retrieving species taxonomic information") as process:
        try:
            response = await parse(request, GBIFPath.SPECIES_TAXONOMIC, parameters_model=GBIFSpeciesTaxonomicParams)
        except Exception as e:
            await context.reply(f"Failed to parse request parameters: {str(e)}")
            return

        params = response.search_parameters
        await process.log(f"Parameters: {params.model_dump()}")
        if not getattr(params, "usageKey", None):
            await context.reply("Usage key is required to retrieve taxonomic information.")
            return
        await process.log(f"Processing request for species with usage key: {params.usageKey}")

        gbif_api = GbifApi()
        urls = gbif_api.build_species_taxonomic_urls(params)

        await process.log(f"Querying {urls} GBIF endpoints to gather taxonomic information...")

        try:
            results = await gbif_api.execute_multiple_requests(urls)

            taxonomic_data = __extract_taxonomic_data(results)

            await process.create_artifact(
                mimetype="application/json",
                description=response.artifact_description,
                uris=[f"https://api.gbif.org/v1/species/{params.usageKey}"],
                metadata={
                    "data_source": "GBIF",
                    "usage_key": params.usageKey,
                    "taxonomic_data": taxonomic_data,
                },
            )

            await context.reply(f"Taxonomic information extraction complete.")

        except Exception as e:
            await process.log(f"Error retrieving taxonomic information: {str(e)}")
            await context.reply(f"Failed to retrieve taxonomic information.") 


def __extract_taxonomic_data(results: dict) -> dict:
    taxonomic_data = {}

    if "basic" in results and "error" not in results["basic"]:
        try:
            basic = NameUsage(**results["basic"])
            taxonomic_data["basic_info"] = {
                "scientific_name": basic.scientificName,
                "canonical_name": basic.canonicalName,
                "rank": basic.rank,
                "taxonomic_status": basic.taxonomicStatus,
                "kingdom": basic.kingdom,
                "phylum": basic.phylum,
                "class": basic.class_,
                "order": basic.order,
                "family": basic.family,
                "genus": basic.genus,
                "is_extinct": basic.isExtinct,
            }
        except Exception as e:
            print(f"Error parsing basic info {e}; adding raw results")
            taxonomic_data["basic_info"] = results["basic"]

    if "parents" in results and "error" not in results["parents"]:
        try:
            parents = [NameUsage(**parent) for parent in results["parents"]]
            taxonomic_data["taxonomic_hierarchy"] = [
                {
                    "rank": parent.rank,
                    "scientific_name": parent.scientificName,
                    "usage_key": parent.key,
                }
                for parent in parents
            ]
        except Exception as e:
            print(f"Error parsing parents {e}; adding raw results")
            taxonomic_data["taxonomic_hierarchy"] = results["parents"]

    if "synonyms" in results and "error" not in results["synonyms"]:
        try:
            synonyms_response = PagingResponseNameUsage(**results["synonyms"])
            taxonomic_data["synonyms"] = {
                "count": synonyms_response.count,
                "results": [
                    {
                        "scientific_name": item.scientificName,
                        "taxonomic_status": item.taxonomicStatus,
                        "usage_key": item.key,
                    }
                    for item in synonyms_response.results
                ],
            }
        except Exception as e:
            print(f"Error parsing synonyms {e}; adding raw results")
            taxonomic_data["synonyms"] = results["synonyms"]

    if "children" in results and "error" not in results["children"]:
        try:
            children_response = PagingResponseNameUsage(**results["children"])
            taxonomic_data["children"] = {
                "count": children_response.count,
                "results": [
                    {
                        "scientific_name": item.scientificName,
                        "rank": item.rank,
                        "usage_key": item.key,
                    }
                    for item in children_response.results
                ],
            }
        except Exception as e:
            print(f"Error parsing children {e}; adding raw results")
            taxonomic_data["children"] = results["children"]

    return taxonomic_data
