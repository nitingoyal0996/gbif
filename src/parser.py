import datetime
import instructor
from enum import Enum
from typing import TypeVar, Type
from src.resources.prompt import SYSTEM_PROMPT, OCCURRENCE_PARAMETER_GUIDELINES, SPECIES_PARAMETER_GUIDELINES

from dotenv import load_dotenv

load_dotenv()


class GBIFPath(Enum):
    OCCURRENCE = "occurrence"
    SPECIES = "species"


PARAMETER_GUIDELINES = {
    GBIFPath.OCCURRENCE: OCCURRENCE_PARAMETER_GUIDELINES,
    GBIFPath.SPECIES: SPECIES_PARAMETER_GUIDELINES,
}


CURRENT_DATE = datetime.datetime.now().strftime("%B %d, %Y")

T = TypeVar("T")


async def parse(
    request: str,
    path: GBIFPath,
    response_model: Type[T],
) -> Type[T]:
    parameter_guidelines = PARAMETER_GUIDELINES[path]

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
