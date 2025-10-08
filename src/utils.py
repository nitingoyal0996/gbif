from pydantic import BaseModel, Field, model_validator
from typing import Optional
import dataclasses
import instructor
import json
from src.log import logger

from src.models.location import Location
from src.gadm.gadm import resolve_to_gadm, GADMMatch


system_prompt = """
You are an expert in taxonomy and geography. Your task is to:
1. Translate organism-related terms to proper scientific nomenclature
2. Extract location references as hierarchical addresses

## MANDATORY Process:

**Step 1: Reasoning (document your thought process)**
In the `reasoning` field, work through:
- What organism-related terms appear in the request?
- What location references appear in the request?
- Which organism terms are common names vs scientific names?
- How do the location references form hierarchical addresses?

**Step 2: Extract taxonomy information**
For EACH organism term you identified:
- Record the `term_found` exactly as it appears in the request
- Set `is_already_scientific` to True or False
- Provide `scientific_name` and `taxonomic_rank` for all terms

**Step 3: Extract location information as hierarchical addresses**
For EACH distinct location mentioned, create ONE hierarchical address object.

**CRITICAL: Locations are hierarchical addresses, not independent entities.**

When user says "Alachua, FL" → This is ONE location with hierarchy:
  - county: "Alachua"
  - state: "Florida" (or "FL")
  - country: "USA" (inferred from FL)
  - country_iso: "US"

When user says "Gainesville, FL and Montreal, Canada" → TWO separate location objects

**Location Structure:**

{
"continent": <if mentioned>,
"country": <if mentioned or can be inferred>,
"country_iso": <ISO code if country known>,
"state": <if mentioned>,
"state_iso": <state code if applicable>,
"county": <if mentioned>,
"locality": <if mentioned>,
"protected_area": <if mentioned>
}

**Rules for Building Hierarchical Addresses:**
1. **Fill in the hierarchy**: If user says "Alachua, FL", infer:
   - county: "Alachua"
   - state: "Florida" 
   - country: "USA" (FL implies USA)
   - country_iso: "US"

2. **Separate location = Separate address object**: "Gainesville, FL and Montreal, Canada" → TWO location objects

3. **Infer missing levels from context**: 
   - "FL" → implies USA
   - "Karnataka" → implies India
   - "Ontario" → implies Canada

4. **Strip type descriptors from names**:
   - "Alachua County" → county: "Alachua" (NOT "Alachua County")
   - "Yellowstone National Park" → protected_area: "Yellowstone"
   - "Pauri district" → county: "Pauri"
   - "Karnataka state" → state: "Karnataka"

5. **Extract full names, not abbreviations (when possible)**:
   - "FL" → state: "Florida", state_iso: "FL"
   - "CA" → state: "California", state_iso: "CA"
   - "NY" → state: "New York", state_iso: "NY"

6. **For comma-separated hierarchies**, put ALL levels in ONE object:
   - "Pauri, Uttarakhand, India" → ONE location: {county: "Pauri", state: "Uttarakhand", country: "India", country_iso: "IN"}

## Location Guidelines:
- **Continent**: Africa, Asia, Europe, North America, South America, Oceania, Antarctica
- **Country**: Use full name + ISO code when possible (e.g., country: "United States", country_iso: "US")
- **State/Province**: First-level administrative divisions (e.g., "California", "Karnataka", "Ontario")
- **County/District**: Second-level administrative divisions (use `county` field for both)
- **Locality**: Cities, towns, specific places
- **Protected Area**: Parks, reserves, sanctuaries

## Taxonomy Guidelines:
- Extract only the organism name itself (e.g., "bird" not "bird species")
- Scientific names should be single taxa, not combinations with "OR", "AND"
- Choose appropriate taxonomic rank
- ALWAYS provide both scientific_name and taxonomic_rank for every term
- You must not repeat records with the same scientific name

## Examples:

Input: "Count beetle species in Brazil"
Output:
- reasoning: "Found 'beetle' as common name (order Coleoptera). Found 'Brazil' as country location."
- organisms: [{'term_found': 'beetle', 'is_already_scientific': False, 'scientific_name': 'Coleoptera', 'taxonomic_rank': 'order'}]
- locations: [{
    'continent': 'South America',
    'country': 'Brazil',
    'country_iso': 'BR'
  }]

Input: "Find monkeys in Karnataka, India"
Output:
- reasoning: "Found 'monkeys' as common name (order Primates). Found hierarchical location 'Karnataka, India' as one address: state Karnataka in country India."
- organisms: [{'term_found': 'monkeys', 'is_already_scientific': False, 'scientific_name': 'Primates', 'taxonomic_rank': 'order'}]
- locations: [{
    'continent': 'Asia',
    'country': 'India',
    'country_iso': 'IN',
    'state': 'Karnataka'
  }]


Input: "Mammals in Gainesville, FL and Montreal, Canada"
Output:
- reasoning: "Found 'mammals' as common name (class Mammalia). Found TWO distinct locations: Gainesville in Florida, USA and Montreal in Canada."
- organisms: [{'term_found': 'mammals', 'is_already_scientific': False, 'scientific_name': 'Mammalia', 'taxonomic_rank': 'class'}]
- locations: [
    {
      'continent': 'North America',
      'country': 'United States',
      'country_iso': 'US',
      'state': 'Florida',
      'state_iso': 'FL',
      'locality': 'Gainesville'
    },
    {
      'continent': 'North America',
      'country': 'Canada',
      'country_iso': 'CA',
      'locality': 'Montreal'
    }
  ]

Input: "Track deer and wolves in Yellowstone National Park"
Output:
- reasoning: "Found 'deer' (family Cervidae) and 'wolves' (species Canis lupus). Found 'Yellowstone National Park' as protected area in USA."
- organisms: [
    {'term_found': 'deer', 'is_already_scientific': False, 'scientific_name': 'Cervidae', 'taxonomic_rank': 'family'},
    {'term_found': 'wolves', 'is_already_scientific': False, 'scientific_name': 'Canis lupus', 'taxonomic_rank': 'species'}
  ]
- locations: [{
    'continent': 'North America',
    'country': 'United States',
    'country_iso': 'US',
    'protected_area': 'Yellowstone'
  }]

Input: "Show birds across Europe and Asia"
Output:
- reasoning: "Found 'birds' as common name (class Aves). Found TWO continent-level locations: Europe and Asia."
- organisms: [{'term_found': 'birds', 'is_already_scientific': False, 'scientific_name': 'Aves', 'taxonomic_rank': 'class'}]
- locations: [
    {'continent': 'Europe'},
    {'continent': 'Asia'}
  ]

Input: "Find Pinus sylvestris in California and Oregon"
Output:
- reasoning: "Found 'Pinus sylvestris' as scientific name (species). Found TWO state locations in USA: California and Oregon."
- organisms: [{'term_found': 'Pinus sylvestris', 'is_already_scientific': True, 'scientific_name': 'Pinus sylvestris', 'taxonomic_rank': 'species'}]
- locations: [
    {
      'continent': 'North America',
      'country': 'United States',
      'country_iso': 'US',
      'state': 'California',
      'state_iso': 'CA'
    },
    {
      'continent': 'North America',
      'country': 'United States',
      'country_iso': 'US',
      'state': 'Oregon',
      'state_iso': 'OR'
    }
  ]

Input: "Records in Amazon rainforest region"
Output:
- reasoning: "No specific organisms mentioned. Found 'Amazon rainforest' as a named ecological region spanning multiple countries in South America."
- organisms: []
- locations: [{
    'continent': 'South America'
  }]

Input: "Show mammals in Uttarakhand districts Pauri and Chamoli"
Output:
- reasoning: "Found 'mammals' as common name (class Mammalia). Found TWO district locations, both in Uttarakhand state, India: Pauri and Chamoli."
- organisms: [{'term_found': 'mammals', 'is_already_scientific': False, 'scientific_name': 'Mammalia', 'taxonomic_rank': 'class'}]
- locations: [
    {
      'continent': 'Asia',
      'country': 'India',
      'country_iso': 'IN',
      'state': 'Uttarakhand',
      'county': 'Pauri'
    },
    {
      'continent': 'Asia',
      'country': 'India',
      'country_iso': 'IN',
      'state': 'Uttarakhand',
      'county': 'Chamoli'
    }
  ]

Input: "Birds observed in New York City"
Output:
- reasoning: "Found 'birds' as common name (class Aves). Found 'New York City' as locality in New York state, USA."
- organisms: [{'term_found': 'birds', 'is_already_scientific': False, 'scientific_name': 'Aves', 'taxonomic_rank': 'class'}]
- locations: [{
    'continent': 'North America',
    'country': 'United States',
    'country_iso': 'US',
    'state': 'New York',
    'state_iso': 'NY',
    'locality': 'New York City'
  }]

Input: "Species in Pauri district, Uttarakhand, India"
Output:
- reasoning: "No specific organisms. Found hierarchical location: Pauri district in Uttarakhand state in India country."
- organisms: []
- locations: [{
    'continent': 'Asia',
    'country': 'India',
    'country_iso': 'IN',
    'state': 'Uttarakhand',
    'county': 'Pauri'
  }]

Input: "Show all records from the past year"
Output:
- reasoning: "No organisms mentioned. No locations mentioned. Request is temporal only."
- organisms: []
- locations: []

Input: "Records in tropical regions"
Output:
- reasoning: "No organisms. 'Tropical regions' is a climate descriptor, not a named geographic location."
- organisms: []
- locations: []

Input: "How many species are in the database?"
Output:
- reasoning: "No specific organisms mentioned. No locations mentioned. General database query."
- organisms: []
- locations: []
"""


class IdentifiedOrganism(BaseModel):
    term_found: str = Field(
        description="The exact organism term as found in the user request (e.g., 'birds', 'monkey', 'Cercopithecidae')",
    )
    is_already_scientific: bool = Field(
        description="True if the term is already in scientific nomenclature, False if it's a common name",
    )
    scientific_name: str = Field(
        description="The scientific name (same as term_found if already scientific, or the translation if common name)",
    )
    taxonomic_rank: str = Field(
        description="The taxonomic rank of the scientific name (e.g., 'species', 'genus', 'family', 'order', 'class')",
    )


class UserRequestExpansion(BaseModel):
    reasoning: str = Field(
        description="Briefly describe: What organism terms found? What locations found? Any translations needed?",
    )
    organisms: list[IdentifiedOrganism] = Field(
        description="All organism terms found with their scientific names and taxonomic ranks",
        default_factory=list,
    )
    locations: list[Location] = Field(
        description="All location references found with their types and names",
        default_factory=list,
    )

    @model_validator(mode="after")
    def validate_unique_scientific_names(self):
        organisms = self.organisms
        seen = set()
        for org in organisms:
            sci_name = org.scientific_name
            if sci_name:
                if sci_name.lower() in seen:
                    raise ValueError(
                        f"Duplicate scientific_name found in organisms: '{sci_name}'. Each scientific_name must be unique."
                    )
                seen.add(sci_name.lower())
        return self


def serialize_for_log(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump(exclude_defaults=True)
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    return str(obj)


async def _generate_resolution_message(
    user_request: str,
    response: BaseModel,
    resolved_fields: dict,
    unresolved_fields: list,
) -> str:

    class ResolutionMessage(BaseModel):
        message: str = Field(
            ...,
            description="a brief message to clarify the search parameters",
        )

    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that crafts a brief message (don't make it an email) to clarify the search parameters. Include what were you able to resolve and what you still need to clarify. It should be a complete sentence.",
            },
            {
                "role": "user",
                "content": f"Generate the message for:\nUser request: {user_request}\nParsed Response: {json.dumps(serialize_for_log(response))}\nResolved fields: {resolved_fields}\nUnresolved fields: {unresolved_fields}.",
            },
        ]
        client = instructor.from_provider(
            "openai/gpt-4.1-nano",
            async_client=True,
        )
        response = await client.chat.completions.create(
            messages=messages,
            response_model=ResolutionMessage,
            max_tokens=100,
            temperature=0.2,
        )
        message_content = response.message
        return message_content

    except Exception as e:
        logger.error(
            f"LLM extraction failed, falling back to default message: {str(e)}"
        )
        return "I encountered an error while trying to generate a message about the clarification required from the user about their search."


async def _generate_artifact_description(details: str) -> str:

    class ArtifactDescription(BaseModel):
        description: Optional[str] = Field(
            description="A concise characterization of the retrieved record statistics.",
            examples=[
                "Occurrence records for species Rattus rattus across multiple countries.",
                "Species-level record counts for observations created in 2025.",
                "Occurrence data for Psittacidae in Alaska, United States.",
                "Per-species record counts for records created in 2025",
            ],
            default=None,
        )

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that summarizes GBIF API search parameters "
                    "into a short, meaningful English description. "
                    "Your output must be a single complete sentence summarizing the type of data retrieved. "
                    "Identify what kind of records (e.g., occurrence records, species counts), "
                    "and mention geographic or taxonomic filters when present. "
                    "Avoid repeating raw parameter names or producing fragments like 'per-country' "
                    "unless multiple countries are explicitly listed."
                ),
            },
            {
                "role": "user",
                "content": f"Generate a clear, natural-language description for this GBIF API request: \nDetails: {details}",
            },
        ]
        client = instructor.from_provider(
            model="openai/gpt-4.1-nano",
            async_client=True,
        )
        response = await client.chat.completions.create(
            messages=messages,
            response_model=ArtifactDescription,
            max_tokens=60,
            temperature=0.2,
        )
        message_content = response.description
        return message_content
    except Exception as e:
        logger.error(
            f"LLM extraction failed, falling back to default description: {str(e)}"
        )
        return "I encountered an error while trying to generate a description of the artifact."


def serialize_organisms(organisms: list) -> list:
    return {org.scientific_name: org.taxonomic_rank for org in organisms}


def serialize_locations(locations: list) -> list:
    """Serialize a list of EnrichedLocation objects to JSON-serializable format."""
    return [loc.model_dump(exclude_none=True) for loc in locations]


async def _preprocess_user_request(user_request: str):
    """
    Translates organism-related terms in user request to scientific nomenclature
    and extracts location information.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User request: {user_request}"},
    ]

    client = instructor.from_provider(
        model="openai/gpt-4.1-unfiltered",
        async_client=True,
        temperature=0.0,
    )

    response = await client.chat.completions.create(
        messages=messages,
        response_model=UserRequestExpansion,
        max_retries=2,
    )

    logger.info(
        f"Identified organisms and locations: {response.model_dump(exclude_none=True)}"
    )
    return response


async def _validate_and_enrich_locations(locations: list) -> list:
    """
    Validates locations against GADM database and enriches with hierarchy and geographic data.

    Args:
        locations: List of Location objects extracted from user request

    Returns:
        List of EnrichedLocation objects with GADM data when available
    """

    class GADMHierarchyLevel(BaseModel):
        """Represents a single level in the GADM administrative hierarchy."""

        name: Optional[str] = Field(
            default=None, description="Administrative division name at this level"
        )
        gid: Optional[str] = Field(
            default=None, description="GADM identifier at this level"
        )

    class GADMHierarchy(BaseModel):
        """Complete GADM administrative hierarchy."""

        level_0: Optional[GADMHierarchyLevel] = Field(
            default=None, description="Country level"
        )
        level_1: Optional[GADMHierarchyLevel] = Field(
            default=None, description="First administrative division (state/province)"
        )
        level_2: Optional[GADMHierarchyLevel] = Field(
            default=None, description="Second administrative division (county/district)"
        )
        level_3: Optional[GADMHierarchyLevel] = Field(
            default=None, description="Third administrative division"
        )

    class EnrichedLocation(BaseModel):
        """Location enriched with GADM validation and hierarchy data."""

        # Original LLM extraction
        original_location: Location = Field(description="Original location from LLM")

        # GADM enrichment
        was_found_in_gadm: bool = Field(
            default=False,
            description="True if location was found and validated in GADM database",
        )
        gadm_gid: Optional[str] = Field(
            default=None, description="GADM ID (e.g., 'USA.11.1_1')"
        )
        gadm_level: Optional[int] = Field(
            default=None,
            description="Administrative level in GADM (0=country, 1=state, etc.)",
        )
        gadm_canonical_name: Optional[str] = Field(
            default=None, description="Canonical name from GADM"
        )
        gadm_hierarchy: Optional[GADMHierarchy] = Field(
            default=None, description="Complete administrative hierarchy from GADM"
        )
        resolution_trace: Optional[list] = Field(
            default=None, description="SQL queries executed during GADM resolution"
        )
        validation_note: Optional[str] = Field(
            default=None,
            description="Notes about validation process (e.g., 'exact match', 'not found')",
        )

    enriched_locations = []

    for loc in locations:
        try:
            # Use new resolve_to_gadm with the Location object directly
            gadm_match: Optional[GADMMatch] = resolve_to_gadm(loc, trace=False)

            if gadm_match:
                # Build hierarchy from GADM match
                hierarchy_dict = gadm_match.hierarchy
                hierarchy = GADMHierarchy(
                    level_0=(
                        GADMHierarchyLevel(
                            name=hierarchy_dict.get("level_0"),
                            gid=(
                                gadm_match.gid.split(".")[0]
                                if "level_0" in hierarchy_dict
                                else None
                            ),
                        )
                        if "level_0" in hierarchy_dict
                        else None
                    ),
                    level_1=(
                        GADMHierarchyLevel(
                            name=hierarchy_dict.get("level_1"),
                            gid=(
                                ".".join(gadm_match.gid.split(".")[:2])
                                if gadm_match.level >= 1 and "level_1" in hierarchy_dict
                                else None
                            ),
                        )
                        if "level_1" in hierarchy_dict
                        else None
                    ),
                    level_2=(
                        GADMHierarchyLevel(
                            name=hierarchy_dict.get("level_2"),
                            gid=(
                                ".".join(gadm_match.gid.split(".")[:3])
                                if gadm_match.level >= 2 and "level_2" in hierarchy_dict
                                else None
                            ),
                        )
                        if "level_2" in hierarchy_dict
                        else None
                    ),
                    level_3=(
                        GADMHierarchyLevel(
                            name=hierarchy_dict.get("level_3"),
                            gid=(
                                gadm_match.gid
                                if gadm_match.level >= 3 and "level_3" in hierarchy_dict
                                else None
                            ),
                        )
                        if "level_3" in hierarchy_dict
                        else None
                    ),
                )

                enriched = EnrichedLocation(
                    original_location=loc,
                    was_found_in_gadm=True,
                    gadm_gid=gadm_match.gid,
                    gadm_level=gadm_match.level,
                    gadm_canonical_name=gadm_match.canonical_name,
                    gadm_hierarchy=hierarchy,
                    resolution_trace=gadm_match.resolution_trace,
                    validation_note="exact match",
                )

                logger.info(
                    f"GADM | Resolved {loc} → {gadm_match.gid} (level {gadm_match.level})"
                )
            else:
                # Not found in GADM - keep original location but mark as unvalidated
                enriched = EnrichedLocation(
                    original_location=loc,
                    was_found_in_gadm=False,
                    validation_note="not found in GADM database",
                )

                logger.warning(f"GADM | Location not found: {loc}")

            enriched_locations.append(enriched)

        except Exception as e:
            # On error, keep original location but mark validation as failed
            logger.error(f"GADM | Error validating {loc}: {str(e)}")
            enriched = EnrichedLocation(
                original_location=loc,
                was_found_in_gadm=False,
                validation_note=f"validation error: {str(e)}",
            )
            enriched_locations.append(enriched)

    return enriched_locations
