from typing import Optional, cast
from typing_extensions import override

from ichatbio.agent import IChatBioAgent
from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentCard
from pydantic import BaseModel

from src.entrypoints import find_occurrence_records, count_occurence_records
from src.models.entrypoints import GBIFOccurrenceSearchParams, GBIFOccurrenceFacetsParams


class GBIFAgent(IChatBioAgent):
    @override
    def get_agent_card(self) -> AgentCard:
        return AgentCard(
            name="GBIF Search",
            description="Searches for information in the GBIF portal (https://gbif.org).",
            icon=None,
            entrypoints=[
                find_occurrence_records.entrypoint,
                count_occurence_records.entrypoint,
            ]
        )

    @override
    async def run(self, context: ResponseContext, request: str, entrypoint: str, params: Optional[BaseModel]):
        match entrypoint:
            case find_occurrence_records.entrypoint.id:
                await find_occurrence_records.run(context, request, cast(GBIFOccurrenceSearchParams, params))
            case count_occurence_records.entrypoint.id:
                await count_occurence_records.run(context, request, cast(GBIFOccurrenceFacetsParams, params))
            case _:
                raise ValueError(f"Unknown entrypoint: {entrypoint}")
