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


async def _expand_user_request(user_request: str):
    """
    Translates organism-related terms in user request to scientific nomenclature.
    """

    class CommonToScientificTranslation(BaseModel):
        common_name: str = Field(
            description="The common name to translate",
        )
        scientific_name: str = Field(
            description="The scientific name to translate to",
        )

    class UserRequestExpansion(BaseModel):
        identified_terms: list[str] = Field(
            description="All organism-related terms (common names, informal names, taxonomic groups) found in the original request",
            default_factory=list,
        )
        taxonomic_translation: list[CommonToScientificTranslation] = Field(
            description="Mapping of identified terms to their scientific names. Example: [{'common_name': 'brown rat', 'scientific_name': 'Rattus norvegicus'}]",
            default_factory=list,
        )
        expanded_request: str = Field(
            description="The user request rewritten with scientific names replacing common names, maintaining the original request structure and intent",
        )
        uncertain_terms: Optional[list[str]] = Field(
            description="Terms that could not be confidently translated or are ambiguous (e.g., 'fish' could be multiple taxa)",
            default=None,
        )

        # @model_validator(mode="after")
        # def validate_translations_in_request(self):
        #     """Ensure all translations made it into the expanded request and common names exist in original request"""
        #     expanded_lower = self.expanded_request.lower()
        #     for translation in self.taxonomic_translation:
        #         if translation.common_name.lower() not in self.expanded_request.lower():
        #             raise ValueError(
        #                 f"Common name '{translation.common_name}' was translated but not found in original request"
        #             )
        #         if translation.scientific_name.lower() not in expanded_lower:
        #             raise ValueError(
        #                 f"Scientific name '{translation.scientific_name}' was translated but not found in expanded_request"
        #             )
        #     return self

    system_prompt = """
You are a taxonomic expert. Your task is to translate organism-related terms in user requests to proper scientific nomenclature.

## MANDATORY Process - Follow Every Step:

**Step 1: Identify organism names**
Find organism references. Extract the core name as it appears in the request.
- If user provides scientific names (e.g., "monkeys (Cercopithecidae)"), recognize these are already scientific
- If user wrote "bird species", identify "bird"

**Step 2: Build translation dictionary**
For EACH common name from Step 1:
- If the user ALREADY provided the scientific name (in parentheses, after "family:", etc.), DO NOT translate
- Only translate if it's PURELY a common name with no scientific equivalent given
- Scientific names should be single taxa, not combinations with "OR", "AND", etc.

**CRITICAL CHECK**: Did you find any common names WITHOUT scientific equivalents provided?
- YES → `taxonomic_translation` MUST have entries
- NO → `taxonomic_translation` is empty []

**Step 3: Rewrite request**
Remove common names if scientific equivalents were provided. Keep logical operators (OR, AND) intact.

## Examples:

Input: "Count beetle species in Brazil"
Step 1: Found "beetle" (no scientific name provided)
Step 2: [{'common_name': 'beetle', 'scientific_name': 'Coleoptera'}]
Step 3: "Count Coleoptera species in Brazil"

Input: "Find monkeys (family:Cercopithecidae OR Hylobatidae) in India"
Step 1: Found "monkeys" but user provided scientific names already
Step 2: []  # No translation needed, scientific names already there
Step 3: "Find Cercopithecidae OR Hylobatidae in India"

Input: "Track deer and wolves"
Step 1: Found "deer" and "wolves" (no scientific names provided)
Step 2: [{'common_name': 'deer', 'scientific_name': 'Cervidae'}, {'common_name': 'wolves', 'scientific_name': 'Canis lupus'}]
Step 3: "Track Cervidae and Canis lupus"

Input: "Show bears (Ursidae) and cats"
Step 1: Found "bears" (has Ursidae), "cats" (no scientific name)
Step 2: [{'common_name': 'cats', 'scientific_name': 'Felidae'}]
Step 3: "Show Ursidae and Felidae"
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
