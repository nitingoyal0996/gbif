"""Tests for GBIF find_occurrence_records entrypoint"""
import pytest
from ichatbio.agent_response import ArtifactResponse
from src.models.entrypoints import BasisOfRecordEnum, ContinentEnum

# Import from parent conftest.py - these are now available as fixtures
from tests.entrypoints.conftest import run_agent_test, assert_valid_artifact_response, assert_process_logs_contain


class TestFindOccurrenceRecords:
    """Tests for the find_occurrence_records entrypoint"""
    
    @pytest.mark.asyncio
    async def test_basic_search(self, context, messages):
        """Test basic occurrence search functionality"""
        params = {"scientificName": ["Puma concolor"], "limit": 10}
        await run_agent_test("find_occurrence_records", params, context, messages)
        
        assert messages, "Agent should yield messages"
        assert_valid_artifact_response(messages, ["data_source", "total_matches"])
        assert_process_logs_contain(messages, "occurrence")

    @pytest.mark.asyncio
    async def test_with_geographic_filters(self, context, messages):
        """Test occurrence search with geographic filters"""
        params = {
            "scientificName": ["Puma concolor"],
            "continent": [ContinentEnum.NORTH_AMERICA],
            "country": ["US"],
            "limit": 20
        }
        await run_agent_test("find_occurrence_records", params, context, messages)
        
        assert_valid_artifact_response(messages, ["portal_url"])

    @pytest.mark.asyncio
    async def test_with_temporal_filters(self, context, messages):
        """Test occurrence search with temporal filters"""
        params = {
            "scientificName": ["Puma concolor"],
            "year": "2020,2021",
            "month": "1,12",
            "limit": 15
        }
        await run_agent_test("find_occurrence_records", params, context, messages)
        
        assert_valid_artifact_response(messages)

    @pytest.mark.asyncio
    async def test_with_basis_of_record_filter(self, context, messages):
        """Test occurrence search with basis of record filter"""
        params = {
            "scientificName": ["Puma concolor"],
            "basisOfRecord": [BasisOfRecordEnum.HUMAN_OBSERVATION],
            "limit": 10
        }
        await run_agent_test("find_occurrence_records", params, context, messages)
        
        assert_valid_artifact_response(messages)

    @pytest.mark.asyncio
    async def test_portal_url_generation(self, context, messages):
        """Test that portal URLs are properly generated"""
        params = {
            "scientificName": ["Puma concolor"],
            "continent": [ContinentEnum.SOUTH_AMERICA],
            "limit": 10
        }
        await run_agent_test("find_occurrence_records", params, context, messages)
        
        artifacts = [m for m in messages if isinstance(m, ArtifactResponse)]
        portal_urls = [m.metadata.get("portal_url") for m in artifacts if m.metadata]
        assert any(url and url.startswith("https://") for url in portal_urls)
        assert any("continent=SOUTH_AMERICA" in url for url in portal_urls if url)
