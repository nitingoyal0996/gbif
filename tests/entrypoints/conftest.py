"""Shared fixtures and configuration for GBIF agent tests"""
import pytest
from ichatbio.agent_response import (
    ArtifactResponse,
    DirectResponse,
    ProcessLogResponse,
    ResponseChannel,
    ResponseContext,
    ResponseMessage
)

from src.agent import GBIFAgent
from src.models.entrypoints import (
    GBIFOccurrenceSearchParams,
    GBIFOccurrenceFacetsParams,
    BasisOfRecordEnum,
    ContinentEnum
)

TEST_CONTEXT_ID = "617727d1-4ce8-4902-884c-db786854b51c"

# Entrypoint configuration for easy extension
ENTRYPOINT_CONFIG = {
    "find_occurrence_records": {
        "params_class": GBIFOccurrenceSearchParams,
        "default_params": {"scientificName": ["Puma concolor"], "limit": 10},
        "expected_metadata_keys": ["data_source", "total_matches", "portal_url"]
    },
    "count_occurrence_records": {
        "params_class": GBIFOccurrenceFacetsParams,
        "default_params": {"scientificName": ["Puma concolor"], "facet": ["country"]},
        "expected_metadata_keys": ["data_source", "facet_fields"]
    }
}


class InMemoryResponseChannel(ResponseChannel):
    def __init__(self, message_buffer: list):
        self.message_buffer = message_buffer

    async def submit(self, message: ResponseMessage, context_id: str):
        self.message_buffer.append(message)


@pytest.fixture(scope="function")
def messages() -> list[ResponseMessage]:
    return []


@pytest.fixture(scope="function")
def context(messages) -> ResponseContext:
    return ResponseContext(InMemoryResponseChannel(messages), TEST_CONTEXT_ID)


@pytest.fixture
def gbif_agent():
    return GBIFAgent()


# Shared helper functions
async def run_agent_test(entrypoint: str, params_dict: dict, context, messages):
    """Helper to run agent with any entrypoint and parameters"""
    agent = GBIFAgent()
    config = ENTRYPOINT_CONFIG[entrypoint]
    params_model = config["params_class"](**params_dict)
    await agent.run(context, request="pytest_query", entrypoint=entrypoint, params=params_model)
    return messages


def assert_valid_artifact_response(messages, expected_keys=None):
    """Helper to validate artifact responses"""
    artifacts = [m for m in messages if isinstance(m, ArtifactResponse)]
    assert artifacts, "Expected at least one ArtifactResponse"
    
    if expected_keys:
        assert any(
            m.metadata and all(key in m.metadata for key in expected_keys)
            for m in artifacts
        ), f"Expected artifact with metadata keys: {expected_keys}"


def assert_process_logs_contain(messages, expected_text):
    """Helper to validate process logs"""
    logs = [m for m in messages if isinstance(m, ProcessLogResponse)]
    assert any(
        expected_text.lower() in m.text.lower() for m in logs
    ), f"Expected process log containing '{expected_text}'"
