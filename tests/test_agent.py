import pytest
from unittest.mock import AsyncMock, patch


def test_get_agent_card(agent):
    card = agent.get_agent_card()

    assert card.name == "GBIF Search"
    assert len(card.entrypoints) == 7


@pytest.mark.asyncio
@patch("src.entrypoints.occurrences.find_occurrence_records.run")
async def test_routes_to_correct_entrypoint(mock_run, agent, context):
    mock_run.return_value = AsyncMock()
    await agent.run(context, "test", "find_occurrence_records", None)
    mock_run.assert_called_once_with(context, "test")


@pytest.mark.asyncio
@patch("src.entrypoints.occurrences.count_occurrence_records.run")
async def test_routes_count_entrypoint(mock_run, agent, context):
    mock_run.return_value = AsyncMock()
    await agent.run(context, "test", "count_occurrence_records", None)
    mock_run.assert_called_once_with(context, "test")


@pytest.mark.asyncio
@patch("src.entrypoints.occurrences.find_occurrence_by_id.run")
async def test_routes_find_occurrence_by_id_entrypoint(mock_run, agent, context):
    mock_run.return_value = AsyncMock()
    await agent.run(context, "test", "find_occurrence_by_id", None)
    mock_run.assert_called_once_with(context, "test")


@pytest.mark.asyncio
@patch("src.entrypoints.species.find_species_records.run")
async def test_routes_find_species_records_entrypoint(mock_run, agent, context):
    mock_run.return_value = AsyncMock()
    await agent.run(context, "test", "find_species_records", None)
    mock_run.assert_called_once_with(context, "test")


@pytest.mark.asyncio
@patch("src.entrypoints.species.count_species_records.run")
async def test_routes_count_species_records_entrypoint(mock_run, agent, context):
    mock_run.return_value = AsyncMock()
    await agent.run(context, "test", "count_species_records", None)
    mock_run.assert_called_once_with(context, "test")


@pytest.mark.asyncio
@patch("src.entrypoints.species.find_species_taxonomic_information.run")
async def test_routes_find_species_taxonomic_information_entrypoint(mock_run, agent, context):
    mock_run.return_value = AsyncMock()
    await agent.run(context, "test", "species_taxonomic_information", None)
    mock_run.assert_called_once_with(context, "test")


@pytest.mark.asyncio
@patch("src.entrypoints.registry.find_datasets.run")
async def test_routes_find_datasets_entrypoint(mock_run, agent, context):
    mock_run.return_value = AsyncMock()
    await agent.run(context, "test", "find_datasets", None)
    mock_run.assert_called_once_with(context, "test")
