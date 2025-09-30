from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request, execute_multiple_requests
from ichatbio.agent_response import IChatBioAgentProcess

"""
Module for resolving taxonomic names to GBIF keys automatically.
"""

import instructor
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple, Any
from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from ichatbio.agent_response import IChatBioAgentProcess

load_dotenv()


class TaxonomicExtraction(BaseModel):
    """Model for LLM-based taxonomic name extraction."""

    families: List[str] = Field(
        default=[],
        description="List of family names mentioned in the text (e.g., Apidae, Felidae, Ursidae)",
    )
    genera: List[str] = Field(
        default=[],
        description="List of genus names mentioned in the text (e.g., Homo, Quercus, Pinus)",
    )
    species: List[str] = Field(
        default=[],
        description="List of species names (binomial) mentioned in the text (e.g., Homo sapiens, Quercus alba)",
    )
    orders: List[str] = Field(
        default=[],
        description="List of order names mentioned in the text (e.g., Primates, Carnivora, Lepidoptera)",
    )
    classes: List[str] = Field(
        default=[],
        description="List of class names mentioned in the text (e.g., Mammalia, Aves, Insecta)",
    )
    phylums: List[str] = Field(
        default=[],
        description="List of phylum names mentioned in the text (e.g., Chordata, Arthropoda, Mollusca)",
    )
    kingdoms: List[str] = Field(
        default=[],
        description="List of kingdom names mentioned in the text (e.g., Animalia, Plantae, Fungi)",
    )
    note: str = Field(
        default="",
        description="Note about the taxonomic names extracted; why you extracted them",
    )


taxonomic_extraction_prompt = """You are a taxonomic expert. Extract all taxonomic names mentioned in the user's request.

- Only extract names that are clearly taxonomic, not common names
- Be conservative - only extract names you're confident about
- Return empty lists for ranks not mentioned in the text

Examples:
- "bees (family: Apidae, Andrenidae)" → families: ["Apidae", "Andrenidae"]
- "Homo sapiens and Pan troglodytes" → species: ["Homo sapiens", "Pan troglodytes"], genera: ["Homo", "Pan"]
- "order Carnivora" → orders: ["Carnivora"]
- "butterflies from family Nymphalidae" → families: ["Nymphalidae"]"""


resolvable_fields = {
    "familyKey": "family",
    "genusKey": "genus",
    "speciesKey": "species",
    "orderKey": "order",
    "classKey": "class",
    "phylumKey": "phylum",
    "kingdomKey": "kingdom",
    # ... add more taxonomic fields here
}


async def resolve_field_from_request(
    api: GbifApi, process: IChatBioAgentProcess, field_name: str, user_request: str
) -> Optional[List[int]]:
    if field_name not in resolvable_fields:
        return None
    rank = resolvable_fields[field_name]
    extraction = await extract_taxonomic_names(process, user_request)
    rank_mapping = {
        "family": extraction.families,
        "genus": extraction.genera,
        "species": extraction.species,
        "order": extraction.orders,
        "class": extraction.classes,
        "phylum": extraction.phylums,
        "kingdom": extraction.kingdoms,
    }
    names = rank_mapping.get(rank, [])
    if not names:
        return None

    resolved_keys = []
    for name in names:
        key = await resolve_name_to_key(api, process, name, rank)
        if key:
            resolved_keys.append(key)
            await process.log(f"Resolved {rank} '{name}' to {key}")
        else:
            await process.log(f"Failed to resolve {rank} '{name}'")
    return resolved_keys if resolved_keys else None


async def extract_taxonomic_names(
    process: IChatBioAgentProcess, user_request: str
) -> TaxonomicExtraction:
    await process.log("Diving deeper...")
    try:
        openai_client = instructor.from_provider(
            "openai/gpt-4.1",
            async_client=True,
        )
        messages = [
            {"role": "system", "content": taxonomic_extraction_prompt},
            {
                "role": "user",
                "content": f"Identified taxonomy: {user_request}",
            },
        ]
        response = await openai_client.chat.completions.create(
            messages=messages,
            response_model=TaxonomicExtraction,
        )
        await process.log(f"Taxonomic names extracted", data=response.model_dump())
        return response
    except Exception as e:
        await process.log(
            f"LLM extraction failed, falling back to empty extraction: {str(e)}"
        )
        return TaxonomicExtraction()


async def resolve_name_to_key(
    api: GbifApi, process: IChatBioAgentProcess, name: str, expected_rank: str
) -> Optional[int]:
    try:
        url = api.build_species_match_url(name)
        await process.log(f"Attempting to resolve {expected_rank} names: {name}", data={'url': url})
        result = await execute_request(url)
        await process.create_artifact(
            mimetype="application/json",
            description=f"GBIF Species Match API call results for: {name}",
            uris=[url],
            metadata={
                "data_source": "GBIF Species Match",
            },
        )
        if result.get("usage") and result.get("usage", {}).get("key"):
            usage = result["usage"]
            key = usage.get("key")
            rank = usage.get("rank", "").lower()
            if rank == expected_rank.upper() or rank == expected_rank.lower():
                return key
            else:
                await process.log(
                    f"Rank mismatch for '{name}' expected {expected_rank}, got {rank}"
                )
                return None
        return None
    except Exception as e:
        await process.log(f"Error resolving '{name}': {str(e)}")
        return None


async def resolve_pending_search_parameters(
    unresolved_params: List[str],
    user_request: str,
    api: GbifApi,
    process: IChatBioAgentProcess,
) -> Tuple[Dict[str, List[int]], List[str]]:
    """
    Attempt to resolve clarification fields automatically.

    Args:
        unresolved_params: List of fields that need clarification
        user_request: Original user request
        api: GBIF API instance
        process: Process for logging

    Returns:
        Tuple of (resolved_fields_dict, remaining_unresolved_fields)
    """
    resolved = {}
    unresolved = []

    for field in unresolved_params:
        resolved_keys = await resolve_field_from_request(
            api, process, field, user_request
        )
        if resolved_keys:
            resolved[field] = resolved_keys
        else:
            unresolved.append(field)
            await process.log(f"Could not auto-resolve {field}")

    return resolved, unresolved


async def resolve_names_to_taxonkeys(
    api: GbifApi, scientific_names: list, process: IChatBioAgentProcess
) -> list:
    """
    Resolve scientific names to GBIF taxon keys using the species match API.

    Note:
        This function uses the GBIF /v2/species/match endpoint for fuzzy name matching.
        Only successfully resolved names will have their taxon keys included in the result.
        Each API call generates an artifact for tracking purposes.
    """
    if not scientific_names:
        return []

    taxon_keys = []

    for name in scientific_names:
        result = None
        try:
            # Use the species match endpoint to resolve the name
            url = api.build_species_match_url(name)
            await process.log(f"URL for name match: {url}")
            result = await execute_request(url)

            # Check if we have a successful match in the 'usage' field
            if result.get("usage") and result.get("usage", {}).get("key"):
                taxon_key = result["usage"]["key"]
                taxon_keys.append(taxon_key)
                await process.create_artifact(
                    mimetype="application/json",
                    description=f"GBIF Species Match API call results for: {name}",
                    uris=[url],
                    metadata={
                        "data_source": "GBIF Species Match",
                    },
                )
            else:
                await process.log(
                    f"No match found for '{name}'",
                    data={
                        "data_source": f"GBIF Species Match results for: {name}",
                        "api_url": url,
                    },
                )

        except Exception as e:
            await process.log(
                f"Failed to resolve name '{name}': {e}",
                data={
                    "data_source": f"GBIF Species Match for: {name}",
                    "error": str(e),
                },
            )
            continue

    await process.log(
        f"Resolved {len(taxon_keys)} out of {len(scientific_names)} names."
    )
    return taxon_keys


async def resolve_keys_to_names(
    api: GbifApi,
    process: IChatBioAgentProcess,
    keys: list,
    type: str,
) -> Dict[int, str]:
    """
    Resolve GBIF usage keys to scientific names using the species API.
    """
    if not keys:
        return {}

    unique_keys: list[int] = sorted({int(k) for k in keys if k is not None})
    urls: Dict[str, str] = {
        str(usage_key): api.build_species_key_search_url(usage_key)
        for usage_key in unique_keys
    }
    await process.log(
        "Resolving GBIF keys to scientific names",
        data={"keys": unique_keys, "type": type},
    )
    results = await execute_multiple_requests(urls)
    keys_to_name: Dict[int, str] = {}
    for key_str, payload in results.items():
        try:
            if isinstance(payload, dict) and "error" not in payload:
                scientific_name = payload.get("scientificName")
                if not scientific_name:
                    scientific_name = payload.get("canonicalName")
                if scientific_name:
                    keys_to_name[int(key_str)] = scientific_name
                else:
                    await process.log(
                        f"No scientific name found for key {key_str}",
                        data={"payload_keys": list(payload.keys())},
                    )
            else:
                await process.log(
                    f"Failed to fetch details for key {key_str}",
                    data={
                        "error": (
                            payload.get("error")
                            if isinstance(payload, dict)
                            else str(payload)
                        )
                    },
                )
        except Exception as e:
            await process.log(
                f"Error processing species details for key {key_str}",
                data={"error": str(e)},
            )

    await process.log(
        "Resolved GBIF keys to names",
        data={"resolved": len(keys_to_name), "requested": len(unique_keys)},
    )

    return keys_to_name
