import datetime
import instructor

from pydantic import BaseModel, Field, create_model
from typing import Type, Optional, List, Dict, Any

from src.resources.prompt_v2 import SYSTEM_PROMPT_V2
from src.resources.fewshot import examples

from dotenv import load_dotenv

load_dotenv()


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


def get_example_messages(entrypoint_id: str) -> List[Dict[str, Any]]:
    # convert the fewshot examples to messages
    messages = []
    for idx, example in enumerate(examples[entrypoint_id]):
        e = f"""
        Example {idx + 1}:
        User Request: {example["response"]["user_request"]}
        Parsed Search Parameters: {example["response"]["search_parameters"] if example["response"]["search_parameters"] else "None"}
        Reasoning: {example["reasoning"]}
        \n\n
        """
        messages.append(e)
    return messages


async def parse(
    request: str,
    entrypoint_id: str,
    parameters_model: Type[BaseModel],
) -> Type[BaseModel]:
    response_model = create_response_model(parameters_model)

    openai_client = instructor.from_provider(
        "openai/gpt-4.1",
        async_client=True,
    )

    prompt = SYSTEM_PROMPT_V2.format(
        CURRENT_DATE=CURRENT_DATE,
    )

    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": "Few shot examples: + "
            + "\n".join(get_example_messages(entrypoint_id)),
        },
        {
            "role": "user",
            "content": f"Generate GBIF Request Parameters for the following user request: {request}",
        },
    ]

    instructor_validation_context = {"user_request": request}

    response = await openai_client.chat.completions.create(
        messages=messages,
        response_model=response_model,
        validation_context=instructor_validation_context,
    )
    return response
