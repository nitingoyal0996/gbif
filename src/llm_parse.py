import instructor
from dotenv import load_dotenv
from src.models.entrypoints import GBIFOccurrenceSearchParams, GBIFOccurrenceFacetsParams

load_dotenv()

async def parse_gbif_occurrence_search_request(request: str) -> GBIFOccurrenceSearchParams:
    openai_client = instructor.from_provider(
        "openai/gpt-4o-mini",
        async_client=True,
    )
    response = await openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that parses requests into GBIFOccurrenceSearchParams objects.",
            },
            {"role": "user", "content": request},
        ],
        response_model=GBIFOccurrenceSearchParams,
    )
    return response.model_dump(exclude_none=True)


async def parse_gbif_occurrence_facets_request(request: str) -> GBIFOccurrenceFacetsParams:
    openai_client = instructor.from_provider(
        "openai/gpt-4o-mini",
        async_client=True,
    )
    response = await openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that parses requests into GBIFOccurrenceFacetsParams objects.",
            },
            {"role": "user", "content": request},
        ],
        response_model=GBIFOccurrenceFacetsParams,
    )
    return response.model_dump(exclude_none=True)
