import datetime
import json
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
    """Convert examples to properly formatted message pairs"""
    messages = []

    for idx, example in enumerate(examples[entrypoint_id]):
        # Add user message (the request)
        messages.append(
            {"role": "user", "content": example["response"]["user_request"]}
        )

        # Add assistant response (structured output + reasoning)
        assistant_content = {
            "search_parameters": example["response"]["search_parameters"],
            "artifact_description": example["response"].get("artifact_description"),
            "reasoning": example["reasoning"],
        }

        messages.append(
            {"role": "assistant", "content": json.dumps(assistant_content, indent=2)}
        )

    return messages


async def parse(
    request: str,
    entrypoint_id: str,
    parameters_model: Type[BaseModel],
) -> Type[BaseModel]:
    response_model = create_response_model(parameters_model)

    openai_client = instructor.from_provider("openai/gpt-4.1", async_client=True)

    # Build messages with proper few-shot structure
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT_V2.format(CURRENT_DATE=CURRENT_DATE),
        }
    ]

    # Add few-shot examples as conversation pairs
    example_messages = get_example_messages(entrypoint_id)
    messages.extend(example_messages)

    messages.append({"role": "user", "content": request})

    response = await openai_client.chat.completions.create(
        messages=messages,
        response_model=response_model,
        validation_context={"user_request": request},
    )
    return response
