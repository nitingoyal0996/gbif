from pydantic import BaseModel, Field, model_validator
from typing import Optional
import dataclasses
import instructor
import json
from src.log import logger
from src.models.location import Location


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
    return [org.model_dump(exclude_none=True, mode="json") for org in organisms]


async def _preprocess_user_request(user_request: str):
    """
    Translates organism-related terms in user request to scientific nomenclature
    and extracts location information.
    """
    with open("src/resources/prompts/preprocess_request.md", "r") as file:
        system_prompt = file.read()

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
