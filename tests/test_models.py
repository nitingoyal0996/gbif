import pytest
from pydantic import ValidationError
from src.models.entrypoints import (
    GBIFOccurrenceSearchParams,
    GBIFOccurrenceFacetsParams,
    BasisOfRecordEnum,
    ContinentEnum,
)

# -------------------------
# Negative Tests (Validation)
# -------------------------

@pytest.mark.parametrize(
    "params",
    [
        {"decimalLatitude": "91,92"},                  # latitude out of range
        {"decimalLongitude": "-181,181"},              # longitude out of range
        {"limit": 301},                                # limit too high
        {"offset": -1},                                # offset negative
        {"basisOfRecord": ["INVALID_TYPE"]},           # invalid enum
        {"continent": ["INVALID_CONTINENT"]},          # invalid enum
        {"datasetKey": ["not-a-uuid"]},                # invalid UUID
    ],
    ids=[
        "latitude_out_of_range",
        "longitude_out_of_range",
        "limit_too_high",
        "offset_negative",
        "invalid_basis_of_record",
        "invalid_continent",
        "invalid_dataset_key",
    ]
)
def test_invalid_base_params(params):
    with pytest.raises(ValidationError):
        GBIFOccurrenceSearchParams(**params)


@pytest.mark.parametrize(
    "params",
    [
        {},  # missing required `facet`
        {"facet": ["country"], "facetMincount": 0},  # facetMincount too low
    ],
    ids=["missing_facet", "facet_mincount_too_low"]
)
def test_invalid_facet_params(params):
    with pytest.raises(ValidationError):
        GBIFOccurrenceFacetsParams(**params)


# -------------------------
# Positive Tests (Valid Inputs)
# -------------------------

def test_search_params_inheritance_defaults():
    params = GBIFOccurrenceSearchParams(
        scientificName=["Quercus robur"],
        basisOfRecord=[BasisOfRecordEnum.PRESERVED_SPECIMEN],
    )
    assert params.scientificName == ["Quercus robur"]
    assert params.basisOfRecord == [BasisOfRecordEnum.PRESERVED_SPECIMEN]
    assert params.limit == 100  # inherited default


def test_facets_params_with_realistic_filters():
    params = GBIFOccurrenceFacetsParams(
        facet=["scientificName", "country", "year"],
        scientificName=["Puma concolor"],
        continent=[
            ContinentEnum.NORTH_AMERICA,
            ContinentEnum.SOUTH_AMERICA
        ],
        year="2020",
        basisOfRecord=[BasisOfRecordEnum.HUMAN_OBSERVATION],
        facetMincount=10,
        facetMultiselect=True,
    )
    assert params.facet == ["scientificName", "country", "year"]
    assert params.scientificName == ["Puma concolor"]
    assert params.continent == [
        ContinentEnum.NORTH_AMERICA,
        ContinentEnum.SOUTH_AMERICA
    ]
    assert params.year == "2020"
    assert params.basisOfRecord == [BasisOfRecordEnum.HUMAN_OBSERVATION]
    assert params.facetMincount == 10
    assert params.facetMultiselect is True
    assert params.limit == 0  # facet model override
