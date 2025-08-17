from typing import Optional
from typing_extensions import override

from ichatbio.agent import IChatBioAgent
from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentCard
from pydantic import BaseModel

from src.entrypoints import (
    find_occurrence_records,
    count_occurence_records,
    find_species_records,
    count_species_records,
    find_species_taxonomic_information,
    find_occurrence_by_id,
    find_datasets,
)
from src.log import logger


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
                find_species_records.entrypoint,
                count_species_records.entrypoint,
                find_species_taxonomic_information.entrypoint,
                find_occurrence_by_id.entrypoint,
                find_datasets.entrypoint,
            ],
        )

    @override
    async def run(
        self,
        context: ResponseContext,
        request: str,
        entrypoint: str,
        params: Optional[BaseModel],
    ):
        logger.info(f"AGENT | Entrypoint={entrypoint} | Request={request}")
        if params:
            logger.info(f"AGENT | Received params: {params}")
        try:
            match entrypoint:
                case find_occurrence_records.entrypoint.id:
                    await find_occurrence_records.run(context, request)
                case count_occurence_records.entrypoint.id:
                    await count_occurence_records.run(context, request)
                case find_species_records.entrypoint.id:
                    await find_species_records.run(context, request)
                case count_species_records.entrypoint.id:
                    await count_species_records.run(context, request)
                case find_species_taxonomic_information.entrypoint.id:
                    await find_species_taxonomic_information.run(context, request)
                case find_occurrence_by_id.entrypoint.id:
                    await find_occurrence_by_id.run(context, request)
                case find_datasets.entrypoint.id:
                    await find_datasets.run(context, request)
                case _:
                    error_msg = f"Unknown entrypoint: {entrypoint}"
                    logger.error(f"AGENT_ERROR | {error_msg}")
                    raise ValueError(error_msg)

        except Exception as e:
            logger.error(
                f"AGENT_ERROR | Entrypoint={entrypoint} | Error={type(e).__name__}: {str(e)}"
            )
            raise
