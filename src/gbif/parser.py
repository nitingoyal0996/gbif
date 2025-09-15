import datetime
import json
import instructor

from pydantic import BaseModel, Field, create_model
from typing import Type, Optional

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


def get_system_prompt(entrypoint_id: str):

    examples = []

    with open("src/resources/fewshot.json", "r") as f:
        fewshot = json.load(f)
        for idx, example in enumerate(fewshot[entrypoint_id]):
            e = f"""
            ### Example {idx + 1}:
            ```json
            {json.dumps(example, indent=2)}
            ```
            """
            examples.append(e)

    prompt = ""

    with open("src/resources/sysprompt.md", "r") as f:
        prompt += f.read()

    prompt += "\n\n## Examples: \n\n" + "\n".join(examples)

    return prompt


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

    messages = [
        {
            "role": "system",
            "content": get_system_prompt(entrypoint_id),
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
        context=instructor_validation_context,
    )
    return response
