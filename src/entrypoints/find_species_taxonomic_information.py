"""
GBIF Species Taxonomic Information Entrypoint

This entrypoint retrieves comprehensive taxonomic information for a specific species
using its GBIF species identifier. Provides detailed taxonomic classification, synonyms,
children taxa, and species profiles.
"""

from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentEntrypoint

from src.api import GbifApi
from src.models.entrypoints import GBIFSpeciesSearchParams, GBIFSpeciesTaxonomicParams
from src.models.enums.species_parameters import TaxonomicStatusEnum, TaxonomicRankEnum
from src.models.responses.species import NameUsage, PagingResponseNameUsage
from src.log import with_logging
from src.parser import parse, GBIFPath
from src.log import logger

from pydantic import BaseModel, Field
from typing import List, Optional

import instructor
from dotenv import load_dotenv

load_dotenv()


entrypoint = AgentEntrypoint(
    id="species_taxonomic_information",
    name="Species Taxonomic Information",
    description="Retrieve comprehensive taxonomic information for a species using its GBIF id",
    examples=[
        "Get taxonomic information for species with id 5231190",
        "Show taxonomic hierarchy and synonyms for species 2476674",
        "Retrieve taxonomic data for species id 2877951 including children taxa",
    ],
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
        gbif_api = GbifApi()

        await process.log(f"Parameters: {params.model_dump()}")
        if not getattr(params, "key", None) and not getattr(params, "name", None):
            await context.reply(
                "Species id or name is required to retrieve taxonomic information."
            )
            return

        if not getattr(params, "key", None):
            await process.log(
                f"No species id found, searching for species by name: {params.name}"
            )
            species_key = await __search_species_by_name(
                gbif_api, request, params.name, process
            )
            params = params.model_copy(update={"key": species_key})

        urls = gbif_api.build_species_taxonomic_urls(params)

        await process.log(f"Querying {urls} GBIF endpoints to gather taxonomic information...")

        try:
            results = await gbif_api.execute_multiple_requests(urls)

            taxonomic_data = __extract_taxonomic_data(results)

            await process.create_artifact(
                mimetype="application/json",
                description=response.artifact_description,
                uris=[f"https://api.gbif.org/v1/species/{params.key}"],
                metadata={
                    "data_source": "GBIF Species",
                    "key": params.key,
                    "data": taxonomic_data,
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
            logger.Error(f"Error parsing basic info {e}; adding raw results")
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
            logger.Error(f"Error parsing parents {e}; adding raw results")
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
            logger.Error(f"Error parsing synonyms {e}; adding raw results")
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
            logger.Error(f"Error parsing children {e}; adding raw results")
            taxonomic_data["children"] = results["children"]

    return taxonomic_data


class SpeciesMatch(BaseModel):
    key: int
    scientificName: str
    canonicalName: Optional[str] = None
    rank: Optional[str] = None
    kingdom: Optional[str] = None
    phylum: Optional[str] = None
    class_: Optional[str] = Field(None, alias="class")
    order: Optional[str] = None
    family: Optional[str] = None
    genus: Optional[str] = None
    isExtinct: Optional[bool] = None


async def __search_species_by_name(
    api: GbifApi, user_query: str, name: str, process: IChatBioAgentProcess
) -> int:
    url = api.build_species_search_url(
        GBIFSpeciesSearchParams(
            q=name, status=TaxonomicStatusEnum.ACCEPTED, rank=TaxonomicRankEnum.SPECIES
        )
    )
    raw_response = await api.execute_request(url)
    await process.log(
        f"Found {len(raw_response.get("results", []))} matches for species name: {name}"
    )

    records = raw_response.get("results", [])
    species_matches: List[SpeciesMatch] = []
    for r in records:
        species_matches.append(
            SpeciesMatch(
                key=r.get("key"),
                scientificName=r.get("scientificName"),
                canonicalName=r.get("canonicalName"),
                rank=r.get("rank"),
                kingdom=r.get("kingdom"),
                phylum=r.get("phylum"),
                class_=r.get("class"),
                order=r.get("order"),
                family=r.get("family"),
                genus=r.get("genus"),
                isExtinct=r.get("isExtinct"),
            )
        )

    if not species_matches:
        raise ValueError(f"No species matches found for name: {name}")

    await process.create_artifact(
        mimetype="application/json",
        description=f"Species matches for provided name: {name}",
        uris=[url],
        metadata={
            "data_source": "GBIF Species",
            "data": species_matches,
        },
    )

    best_match = await __find_best_match(species_matches, user_query)
    await process.log(f"Selected match: {best_match.model_dump_json()}")
    return best_match.key


async def __find_best_match(
    species_matches: List[SpeciesMatch], user_query: str
) -> SpeciesMatch:

    client = instructor.from_provider(
        "openai/gpt-4o",
        async_client=True,
    )

    response = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful biodiversity researcher assistant that finds the best match for a species name for the user query. You will be given a user query and a dictionary of species keys and details. You will need to return the best match.",
            },
            {
                "role": "user",
                "content": f"User query: {user_query}\n\nSpecies name to key: {species_matches}",
            },
        ],
        response_model=SpeciesMatch,
    )

    return response
