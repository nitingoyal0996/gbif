import datetime
import instructor

from enum import Enum
from pydantic import BaseModel, Field, create_model
from typing import Type, Optional, List, Dict, Any

from src.resources.prompt import (
    SYSTEM_PROMPT,
    OCCURRENCE_PARAMETER_GUIDELINES,
    SPECIES_PARAMETER_GUIDELINES,
    SPECIES_TAXONOMIC_PARAMETER_GUIDELINES,
    REGISTRY_PARAMETER_GUIDELINES,
    FIELD_NUANCES,
)

from dotenv import load_dotenv

load_dotenv()


class GBIFPath(Enum):
    OCCURRENCE = "occurrence"
    SPECIES = "species"
    SPECIES_TAXONOMIC = "species_taxonomic"
    OCCURRENCE_BY_ID = "occurrence_by_id"
    REGISTRY = "registry"


PARAMETER_GUIDELINES = {
    GBIFPath.OCCURRENCE: OCCURRENCE_PARAMETER_GUIDELINES,
    GBIFPath.SPECIES: SPECIES_PARAMETER_GUIDELINES,
    GBIFPath.SPECIES_TAXONOMIC: SPECIES_TAXONOMIC_PARAMETER_GUIDELINES,
    GBIFPath.OCCURRENCE_BY_ID: OCCURRENCE_PARAMETER_GUIDELINES,
    GBIFPath.REGISTRY: REGISTRY_PARAMETER_GUIDELINES,
}


CURRENT_DATE = datetime.datetime.now().strftime("%B %d, %Y")


def create_response_model(parameter_model: Type[BaseModel]) -> Type[BaseModel]:
    return create_model(
        "LLMResponse",
        search_parameters=(
            Optional[parameter_model],
            Field(
                description="The search parameters for the API",
                default=None,
            ),
        ),
        artifact_description=(
            Optional[str],
            Field(
                description="A concise characterization of the retrieved record statistics",
                examples=[
                    "Per-country record counts for species Rattus rattus",
                    "Per-species record counts for records created in 2025",
                ],
                default=None,
            ),
        ),
        clarification_needed=(
            Optional[bool],
            Field(
                description="If you are unable to determine the parameter for the value provided in the user request, set this to True",
                default=None,
            ),
        ),
        clarification_reason=(
            Optional[str],
            Field(
                description="The reason or a short note why the user request needs clarification about the parameter values",
                default=None,
            ),
        ),
        __base__=BaseModel,
    )


async def parse(
    request: str,
    path: GBIFPath,
    parameters_model: Type[BaseModel],
) -> Type[BaseModel]:
    parameter_guidelines = PARAMETER_GUIDELINES[path]
    response_model = create_response_model(parameters_model)

    openai_client = instructor.from_provider(
        "openai/gpt-4.1",
        async_client=True,
    )
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(
                CURRENT_DATE=CURRENT_DATE,
                PARAMETER_GUIDELINES=parameter_guidelines,
                FIELD_NUANCES=FIELD_NUANCES,
            ),
        },
        {"role": "user", "content": f"user request: {request}"},
    ]

    response = await openai_client.chat.completions.create(
        messages=messages,
        response_model=response_model,
    )
    return response
