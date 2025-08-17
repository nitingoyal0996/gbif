from src.gbif.api import GbifApi
from src.gbif.fetch import execute_request
from ichatbio.agent_response import IChatBioAgentProcess


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
            await process.log(f"Resolving scientific name: {name}")

            # Use the species match endpoint to resolve the name
            url = api.build_species_match_url(name)
            result = await execute_request(url)
            print(f"Species Match API call result: {result}")

            # Check if we have a successful match in the 'usage' field
            if result.get("usage") and result.get("usage", {}).get("key"):
                taxon_key = result["usage"]["key"]
                taxon_keys.append(taxon_key)
                await process.log(
                    f"Successfully resolved '{name}' to taxon key: {taxon_key}"
                )
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
        f"Taxonomic resolution complete. Resolved {len(taxon_keys)} out of {len(scientific_names)} names."
    )
    return taxon_keys
