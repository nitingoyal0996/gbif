from pydantic import BaseModel, model_validator, ValidationInfo, field_validator
from typing import ClassVar
from src.models.entrypoints import (
    GBIFOccurrenceSearchParams,
    GBIFOccurrenceByIdParams,
    GBIFSpeciesSearchParams,
    GBIFSpeciesTaxonomicParams,
    GBIFDatasetSearchParams,
    GBIFOccurrenceFacetsParams,
    GBIFSpeciesFacetsParams,
)


class RequestValidationMixin(BaseModel):
    """Generic mixin to ensure model values appear in the original user request."""

    # Override this in subclasses
    VALIDATION_FIELDS: ClassVar[dict[str, str]] = {}

    @model_validator(mode="after")
    def validate_values_are_from_request(self, info: ValidationInfo):
        user_request = (info.context or {}).get("user_request")
        if not user_request:
            return self

        values = self.model_dump()

        # Validate that all provided parameters are valid and present in the model
        valid_fields = set(type(self).model_fields.keys())
        for key in values.keys():
            if key not in valid_fields:
                raise ValueError(
                    f"Invalid parameter '{key}' provided. "
                    f"Allowed parameters are: {sorted(valid_fields)}"
                )

        if not any(values.values()):
            raise ValueError("No values provided for any parameter")

        for field, value in values.items():
            if value is None or field not in self.VALIDATION_FIELDS:
                continue

            # normalize scalar → list
            candidates = value if isinstance(value, list) else [value]
            for v in candidates:
                if str(v).lower() not in user_request.lower():
                    context = self.VALIDATION_FIELDS[field]
                    raise ValueError(
                        f"The value '{v}' for field '{field}' ({context}) "
                        f"was not found in the original request. "
                        "You must provide explicit values; they cannot be inferred or made up."
                    )
        return self


class FacetValidationMixin:
    @classmethod
    def allowed_facet_fields(cls):
        exclude = {"facet", "facetMincount", "facetMultiselect", "limit", "offset"}
        return {f for f in cls.model_fields.keys() if f not in exclude}

    @field_validator("facet")
    @classmethod
    def validate_facet_names(cls, v):
        allowed = cls.allowed_facet_fields()
        invalid = [f for f in v if f not in allowed]
        if invalid:
            raise ValueError(
                f"Invalid facet(s): {invalid}. Allowed facets are: {sorted(allowed)}"
            )
        return v


class OccurrenceSearchParamsValidator(
    RequestValidationMixin, GBIFOccurrenceSearchParams
):
    VALIDATION_FIELDS: ClassVar[dict[str, str]] = {
        "decimalLatitude": "latitude/longitude",
        "decimalLongitude": "latitude/longitude",
        "taxonKey": "key or ID",
        "datasetKey": "key or ID",
        "kingdomKey": "key or ID",
        "phylumKey": "key or ID",
        "classKey": "key or ID",
        "orderKey": "key or ID",
        "familyKey": "key or ID",
        "speciesKey": "key or ID",
        "genusKey": "key or ID",
        "occurrenceId": "key or ID",
        "eventId": "key or ID",
        "recordNumber": "key or ID",
        "collectionCode": "key or ID",
        "institutionCode": "key or ID",
        "catalogNumber": "key or ID",
    }


class OccurrenceFacetsParamsValidator(
    OccurrenceSearchParamsValidator, GBIFOccurrenceFacetsParams, FacetValidationMixin
):
    pass


class OccurrenceSearchByIdParamsValidator(RequestValidationMixin, GBIFOccurrenceByIdParams):
    VALIDATION_FIELDS: ClassVar[dict[str, str]] = {
        "gbifId": "key or ID",
    }


class SpeciesSearchParamsValidator(RequestValidationMixin, GBIFSpeciesSearchParams):
    VALIDATION_FIELDS: ClassVar[dict[str, str]] = {
        "higherTaxonKey": "key or ID",
        "datasetKey": "key or ID",
        "constituentKey": "key or ID",
    }


class SpeciesFacetsParamsValidator(
    SpeciesSearchParamsValidator, GBIFSpeciesFacetsParams
):
    pass


class SpeciesTaxonomicParamsValidator(
    RequestValidationMixin, GBIFSpeciesTaxonomicParams
):
    VALIDATION_FIELDS: ClassVar[dict[str, str]] = {
        "key": "key or ID",
    }


class DatasetSearchParamsValidator(RequestValidationMixin, GBIFDatasetSearchParams):
    VALIDATION_FIELDS: ClassVar[dict[str, str]] = {
        "projectId": "key or ID",
        "taxonKey": "key or ID",
        "recordCount": "number",
        "networkKey": "key or ID",
        "endorsingNodeKey": "key or ID",
        "installationKey": "key or ID",
        "contactUserId": "key or ID",
    }
