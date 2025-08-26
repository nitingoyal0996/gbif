import pytest
from pydantic import ValidationError
from src.models.entrypoints import (
    GBIFOccurrenceSearchParams,
    GBIFOccurrenceFacetsParams,
    BasisOfRecordEnum,
)


def test_valid_basic_params():
    # Test creation with basic valid parameters
    params = GBIFOccurrenceSearchParams(
        scientificName=["Quercus robur"],
        basisOfRecord=[BasisOfRecordEnum.PRESERVED_SPECIMEN],
    )
    assert params.limit == 100  # inherited default
    assert params.scientificName == ["Quercus robur"]


@pytest.mark.parametrize(
    "invalid_data, expected_error",
    [
        ({"decimalLatitude": "91,92"}, "latitude must be between -90 and 90"),
        ({"limit": 301}, "input should be less than or equal to 300"),
    ],
)
def test_validation_errors(invalid_data, expected_error):
    # Test various validation error scenarios
    with pytest.raises(ValidationError) as exc_info:
        GBIFOccurrenceSearchParams(**invalid_data)
    assert expected_error in str(exc_info.value).lower()


def test_valid_facets_configuration():
    # Test creation with valid facet parameters
    params = GBIFOccurrenceFacetsParams(
        facet=["scientificName", "country"],
        facetMincount=10,
        scientificName=["Puma concolor"],
    )
    assert params.limit == 0  # facet model override
    assert params.facetMincount == 10


def test_required_facet_parameter():
    # Test that facet parameter is required
    with pytest.raises(ValidationError) as exc_info:
        GBIFOccurrenceFacetsParams()
    assert "facet" in str(exc_info.value).lower()
