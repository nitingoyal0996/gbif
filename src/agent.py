from typing import Optional
from typing_extensions import override

from ichatbio.agent import IChatBioAgent
from ichatbio.agent_response import ResponseContext
from ichatbio.types import AgentCard
from pydantic import BaseModel

from src.entrypoints import occurrences, species, registry
from src.log import logger


class GBIFAgent(IChatBioAgent):
    @override
    def get_agent_card(self) -> AgentCard:
        return AgentCard(
            name="GBIF Search",
            description="Searches for information in the GBIF portal (https://gbif.org).",
            icon=None,
            entrypoints=[
                occurrences.search.entrypoint,
                occurrences.count.entrypoint,
                species.search.entrypoint,
                species.count.entrypoint,
                species.search_taxa.entrypoint,
                occurrences.search_by_id.entrypoint,
                registry.search.entrypoint,
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
                case occurrences.search.entrypoint.id:
                    await occurrences.search.run(context, request)
                case occurrences.count.entrypoint.id:
                    await occurrences.count.run(context, request)
                case species.search.entrypoint.id:
                    await species.search.run(context, request)
                case species.count.entrypoint.id:
                    await species.count.run(context, request)
                case species.search_taxa.entrypoint.id:
                    await species.search_taxa.run(context, request)
                case occurrences.search_by_id.entrypoint.id:
                    await occurrences.search_by_id.run(context, request)
                case registry.search.entrypoint.id:
                    await registry.search.run(context, request)
                case _:
                    error_msg = f"Unknown entrypoint: {entrypoint}"
                    logger.error(f"AGENT_ERROR | {error_msg}")
                    raise ValueError(error_msg)

        except Exception as e:
            logger.error(
                f"AGENT_ERROR | Entrypoint={entrypoint} | Error={type(e).__name__}: {str(e)}"
            )
            raise
