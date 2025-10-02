from pydantic import BaseModel, Field, model_validator
from typing import Optional
import instructor
import json
import logging
import dataclasses

logger = logging.getLogger(__name__)


def serialize_for_log(obj):
    # Pydantic v2
    if hasattr(obj, "model_dump"):
        return obj.model_dump(exclude_defaults=True)
    # Dataclass
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    # Fallback
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


async def _generate_artifact_description(search_parameters: str) -> str:

    class ArtifactDescription(BaseModel):
        description: Optional[str] = Field(
            description="A concise characterization of the retrieved record statistics.",
            examples=[
                "Per-country record counts for species Rattus rattus",
                "Per-species record counts for records created in 2025",
            ],
            default=None,
        )

    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that crafts a brief yet meaningful description of the artifact based on request parameters. It should be a complete sentence.",
            },
            {
                "role": "user",
                "content": f"Generate description for request: \nParameters: {search_parameters}",
            },
        ]
        client = instructor.from_provider(
            model="openai/gpt-4.1-nano",
            async_client=True,
        )
        response = await client.chat.completions.create(
            messages=messages,
            response_model=ArtifactDescription,
            max_tokens=50,
            temperature=0.2,
        )
        message_content = response.description
        return message_content
    except Exception as e:
        logger.error(
            f"LLM extraction failed, falling back to default description: {str(e)}"
        )
        return "I encountered an error while trying to generate a description of the artifact."


async def _identify_organisms(user_request: str):
    """
    Translates organism-related terms in user request to scientific nomenclature.
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
            description="Briefly describe the thought process: What organism terms did you find? Which are common names vs scientific? What translations are needed?",
        )
        organisms: list[IdentifiedOrganism] = Field(
            description="All organism terms found with their scientific names and taxonomic ranks",
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

    system_prompt = """
You are a taxonomic expert. Your task is to translate organism-related terms in user requests to proper scientific nomenclature.

## MANDATORY Process:

**Step 1: Reasoning (document your thought process)**
In the `reasoning` field, work through these questions:
- What organism-related terms appear in the request?
- Which terms are already scientific names vs common names?
- For common names, what are the appropriate scientific names and ranks?
- For scientific names already present, what are their taxonomic ranks?
- Are there any ambiguous terms?

**Step 2: Extract taxonomy information**
For EACH organism term you identified:
- Record the `term_found` exactly as it appears in the request
- Set `is_already_scientific` to True or False
- If False (common name): provide translated `scientific_name` and `taxonomic_rank`
- If True (already scientific): provide the same `scientific_name` (= term_found) and determine its `taxonomic_rank`

**Step 3: Rewrite request**
Replace common names with scientific names. Keep scientific names as-is. Preserve all logical operators (OR, AND) and other request structure.

## Guidelines:
- Extract only the organism name itself (e.g., "bird" not "bird species")
- Scientific names should be single taxa, not combinations with "OR", "AND"
- Choose appropriate taxonomic rank:
  - Specific animals/plants → species or genus (e.g., "brown rat" → "Rattus norvegicus", species)
  - General groups → family, order, or class (e.g., "beetles" → "Coleoptera", order)
- If term has scientific name in parentheses like "birds (Aves)", recognize Aves is already provided
- ALWAYS provide both scientific_name and taxonomic_rank for every term
- You must not repeat records with the same scientific name

## Examples:

Input: "Count beetle species in Brazil"
Output:
- reasoning: "Found 'beetle' as an organism term. It's a common name for the order Coleoptera. No scientific names were provided."
- taxonomy: [{'term_found': 'beetle', 'is_already_scientific': False, 'scientific_name': 'Coleoptera', 'taxonomic_rank': 'order'}]

Input: "Find monkeys (family:Cercopithecidae OR Hylobatidae) in India"
Output:
- reasoning: "Found 'monkeys' as common name, but user already provided the scientific families Cercopithecidae and Hylobatidae. Also found these two family names explicitly. The families are already in scientific nomenclature."
- taxonomy: [
    {'term_found': 'monkeys', 'is_already_scientific': False, 'scientific_name': 'Primates', 'taxonomic_rank': 'order'},
    {'term_found': 'Cercopithecidae', 'is_already_scientific': True, 'scientific_name': 'Cercopithecidae', 'taxonomic_rank': 'family'},
    {'term_found': 'Hylobatidae', 'is_already_scientific': True, 'scientific_name': 'Hylobatidae', 'taxonomic_rank': 'family'}
  ]

Input: "Track deer and wolves"
Output:
- reasoning: "Found two organism terms: 'deer' and 'wolves'. Both are common names. 'Deer' refers to family Cervidae. 'Wolves' is the common name for species Canis lupus."
- taxonomy: [
    {'term_found': 'deer', 'is_already_scientific': False, 'scientific_name': 'Cervidae', 'taxonomic_rank': 'family'},
    {'term_found': 'wolves', 'is_already_scientific': False, 'scientific_name': 'Canis lupus', 'taxonomic_rank': 'species'}
  ]

Input: "Show bears (Ursidae) and cats"
Output:
- reasoning: "Found 'bears' with Ursidae in parentheses - the scientific name is already provided. Found 'cats' as a common name without scientific equivalent, which refers to family Felidae. Also explicitly found 'Ursidae' which is a family."
- taxonomy: [
    {'term_found': 'bears', 'is_already_scientific': False, 'scientific_name': 'Ursidae', 'taxonomic_rank': 'family'},
    {'term_found': 'Ursidae', 'is_already_scientific': True, 'scientific_name': 'Ursidae', 'taxonomic_rank': 'family'},
    {'term_found': 'cats', 'is_already_scientific': False, 'scientific_name': 'Felidae', 'taxonomic_rank': 'family'}
  ]

Input: "Find Pinus sylvestris and oak trees in Europe"
Output:
- reasoning: "Found 'Pinus sylvestris' which is already a scientific binomial name (species). Found 'oak trees' where 'oak' is a common name for genus Quercus."
- taxonomy: [
    {'term_found': 'Pinus sylvestris', 'is_already_scientific': True, 'scientific_name': 'Pinus sylvestris', 'taxonomic_rank': 'species'},
    {'term_found': 'oak', 'is_already_scientific': False, 'scientific_name': 'Quercus', 'taxonomic_rank': 'genus'}
  ]

Input: "Show birds and Mammalia in Australia"
Output:
- reasoning: "Found 'birds' as a common name for class Aves. Found 'Mammalia' which is already the scientific name for the mammal class."
- taxonomy: [
    {'term_found': 'birds', 'is_already_scientific': False, 'scientific_name': 'Aves', 'taxonomic_rank': 'class'},
    {'term_found': 'Mammalia', 'is_already_scientific': True, 'scientific_name': 'Mammalia', 'taxonomic_rank': 'class'}
  ]
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

    return response
