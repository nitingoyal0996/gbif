import pytest
from src.api import GbifApi
from src.models.entrypoints import GBIFOccurrenceSearchParams, GBIFOccurrenceFacetsParams
from src.models.gbif import (
    BasisOfRecordEnum,
    ContinentEnum,
    OccurrenceStatusEnum,
    LicenseEnum,
    MediaObjectTypeEnum,
)

@pytest.fixture
def api():
    return GbifApi()

def test_api_initialization(api):
    assert api.base_url == "https://api.gbif.org/v1"
    assert api.portal_url == "https://gbif.org"
    assert api.config["timeout"] == 30
    assert api.config["max_retries"] == 3

def test_convert_to_api_params(api):
    basic_params = GBIFOccurrenceSearchParams( # type: ignore
        q="Quercus robur",
        scientificName=["Quercus robur"],
        limit=10
    )
    basic_result = api._convert_to_api_params(basic_params)
    assert basic_result["q"] == "Quercus robur"
    assert basic_result["scientificName"] == ["Quercus robur"]
    assert basic_result["limit"] == 10
    assert "offset" not in basic_result

    enum_params = GBIFOccurrenceSearchParams( # type: ignore
        basisOfRecord=[BasisOfRecordEnum.PRESERVED_SPECIMEN],
        continent=[ContinentEnum.EUROPE],
        occurrenceStatus=OccurrenceStatusEnum.PRESENT,
        license=[LicenseEnum.CC0_1_0],
        mediaType=[MediaObjectTypeEnum.StillImage]
    )
    enum_result = api._convert_to_api_params(enum_params)
    assert enum_result["basisOfRecord"] == ["PRESERVED_SPECIMEN"]
    assert enum_result["continent"] == ["EUROPE"]
    assert enum_result["occurrenceStatus"] == "PRESENT"
    assert enum_result["license"] == ["CC0_1_0"]
    assert enum_result["mediaType"] == ["StillImage"]

def test_url_building(api):
    """Test URL building for different endpoints."""
    # Test search URL
    search_params = GBIFOccurrenceSearchParams( # type: ignore
        q="Quercus robur",
        limit=5,
        offset=10
    )
    search_url = api.build_occurrence_search_url(search_params)
    assert search_url.startswith("https://api.gbif.org/v1/occurrence/search?")
    assert "q=Quercus+robur" in search_url
    assert "limit=5" in search_url
    assert "offset=10" in search_url

    # Test facets URL
    facets_params = GBIFOccurrenceFacetsParams( # type: ignore
        q="fox",
        facet=["kingdom", "country"],
        facetMincount=5
    )
    facets_url = api.build_occurrence_facets_url(facets_params)
    assert facets_url.startswith("https://api.gbif.org/v1/occurrence/search?")
    assert "facet=country" in facets_url
    assert "facetMincount=5" in facets_url
    # Test portal URL conversion
    api_url = "https://api.gbif.org/v1/occurrence/search?q=test"
    portal_url = api.build_portal_url(api_url)
    assert portal_url == "https://gbif.org/occurrence/search?q=test"

def test_response_formatting(api):
    """Test response summary formatting."""
    # Test empty response
    assert api.format_response_summary({}) == "No data returned"

    # Test no records
    assert api.format_response_summary({"count": 0}) == "No records found"

    # Test count only
    assert api.format_response_summary({"count": 100}) == "Found 100 total records"

    # Test count with results
    response = {
        "count": 100,
        "results": [{"key": 1}, {"key": 2}]
    }
    assert api.format_response_summary(response) == "Found 100 total records (returned 2)"

def test_complex_search_params(api):
    """Test complex search parameters with multiple filters."""
    params = GBIFOccurrenceSearchParams( # type: ignore
        q="mammal",
        scientificName=["Homo sapiens"],
        basisOfRecord=[BasisOfRecordEnum.HUMAN_OBSERVATION],
        continent=[ContinentEnum.EUROPE],
        country=["US"],
        year="2020,2023",
        decimalLatitude="30,50",
        decimalLongitude="-100,-50",
        hasCoordinate=True,
        occurrenceStatus=OccurrenceStatusEnum.PRESENT,
        license=[LicenseEnum.CC0_1_0],
        limit=20,
        offset=40
    )
    
    api_params = api._convert_to_api_params(params)
    
    # Verify key parameters are correctly converted
    assert api_params["q"] == "mammal"
    assert api_params["scientificName"] == ["Homo sapiens"]
    assert api_params["basisOfRecord"] == ["HUMAN_OBSERVATION"]
    assert api_params["continent"] == ["EUROPE"]
    assert api_params["country"] == ["US"]
    assert api_params["year"] == "2020,2023"
    assert api_params["decimalLatitude"] == "30,50"
    assert api_params["decimalLongitude"] == "-100,-50"
    assert api_params["hasCoordinate"] is True
    assert api_params["occurrenceStatus"] == "PRESENT"
    assert api_params["license"] == ["CC0_1_0"]
    assert api_params["limit"] == 20
    assert api_params["offset"] == 40 