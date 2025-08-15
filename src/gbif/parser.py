import datetime
import instructor

from enum import Enum
from pydantic import BaseModel, Field, create_model
from typing import Type

from src.resources.prompt import (
    SYSTEM_PROMPT,
    OCCURRENCE_PARAMETER_GUIDELINES,
    SPECIES_PARAMETER_GUIDELINES,
    SPECIES_TAXONOMIC_PARAMETER_GUIDELINES,
)

from dotenv import load_dotenv

load_dotenv()


class GBIFPath(Enum):
    OCCURRENCE = "occurrence"
    SPECIES = "species"
    SPECIES_TAXONOMIC = "species_taxonomic"


PARAMETER_GUIDELINES = {
    GBIFPath.OCCURRENCE: OCCURRENCE_PARAMETER_GUIDELINES,
    GBIFPath.SPECIES: SPECIES_PARAMETER_GUIDELINES,
    GBIFPath.SPECIES_TAXONOMIC: SPECIES_TAXONOMIC_PARAMETER_GUIDELINES,
}


CURRENT_DATE = datetime.datetime.now().strftime("%B %d, %Y")


def create_response_model(parameter_model: Type[BaseModel]) -> Type[BaseModel]:
    return create_model(
        "LLMResponse",
        search_parameters=(
            parameter_model,
            Field(description="The search parameters for the API"),
        ),
        artifact_description=(
            str,
            Field(
                description="A concise characterization of the retrieved record statistics",
                examples=[
                    "Per-country record counts for species Rattus rattus",
                    "Per-species record counts for records created in 2025",
                ],
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
    response = await openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(
                    CURRENT_DATE=CURRENT_DATE, PARAMETER_GUIDELINES=parameter_guidelines
                ),
            },
            {"role": "user", "content": request},
        ],
        response_model=response_model,
    )
    return response
