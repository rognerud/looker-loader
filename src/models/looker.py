from typing import List, Optional, Union
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError
import warnings

from src.enums import (
    # LookerJoinType,
    LookerMeasureType,
    # LookerRelationshipType,
    LookerTimeFrame,
    LookerValueFormatName,
)

#  metaclass
class LookerBase(BaseModel):
    label: Optional[str] = None
    hidden: Optional[bool] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

#  metaclass
class LookerViewElement(LookerBase):
    """Looker data for a view element."""
    name: str = Field(default=None)
    type: str = Field(default=None)

    value_format_name: Optional[LookerValueFormatName] = Field(default=None)
    group_label: Optional[str] = None

    @field_validator("value_format_name", mode="before")
    def validate_format_name(cls, value):
        if value is not None:
            if isinstance(value, str):
                value = value.strip()
                if not LookerValueFormatName.has_value(value):
                    warnings.warn(
                        f"Invalid value for value_format_name [{value}]. Setting to None. ",
                    )
                    return None
                else:
                    return LookerValueFormatName(value)
        return value

class LookerMeasureFilter(BaseModel):
    filter_dimension: str
    filter_expression: str

class LookerMeasure(LookerViewElement):
    """Looker data for a measure.
    
    :
        looker:
            measures:
    """

    # Required fields
    type: LookerMeasureType

    # Common optional fields
    name: Optional[str] = None

    # Fields specific to certain measure types
    approximate: Optional[bool] = None  # For count_distinct
    approximate_threshold: Optional[int] = None  # For count_distinct
    precision: Optional[int] = None  # For average, sum
    sql_distinct_key: Optional[str] = None  # For count_distinct
    percentile: Optional[int] = None  # For percentile measures
    required_access_grants: Optional[List[str]] = Field(default=None)
    filters: Optional[List[LookerMeasureFilter]] = None

    @model_validator(mode="before")
    def validate_measure_attributes(cls, values):
        """Validate that measure attributes are compatible with the measure type."""
        if type(values) is dict:
            measure_type = values.get("type")

            if any(
                v is not None
                for v in [
                    values.get("approximate"),
                    values.get("approximate_threshold"),
                    values.get("sql_distinct_key"),
                ]
            ) and measure_type not in (
                LookerMeasureType.COUNT_DISTINCT,
                LookerMeasureType.SUM_DISTINCT,
            ):
                raise ValueError(
                    "approximate, approximate_threshold, and sql_distinct_key can only be used with distinct measures"
                )

            if values.get(
                "percentile"
            ) is not None and not measure_type.value.startswith("percentile"):
                raise ValueError("percentile can only be used with percentile measures")

            if values.get("precision") is not None and measure_type not in [
                LookerMeasureType.AVERAGE,
                LookerMeasureType.SUM,
            ]:
                raise ValueError(
                    "precision can only be used with average or sum measures"
                )

        return values

class LookerDimension(LookerViewElement):
    """Looker-specific data for a dimension on a model column

        looker:
            dimension:

    """

    convert_tz: Optional[bool] = Field(default=None)
    timeframes: Optional[List[LookerTimeFrame]] = Field(default=None)
    can_filter: Optional[Union[bool, str]] = Field(default=None)
    group_item_label: Optional[str] = Field(default=None)
    order_by_field: Optional[str] = Field(default=None)
    suggestable: Optional[bool] = Field(default=None)
    case_sensitive: Optional[bool] = Field(default=None)
    allow_fill: Optional[bool] = Field(default=None)
    required_access_grants: Optional[List[str]] = Field(default=None)
    html: Optional[bool] = Field(default=None)
    tag_append: Optional[List[str]] = None
    description_append: Optional[str] = None
    description_prepend: Optional[str] = None
    fields: Optional[List['LookerDimension']] = None
    sql: Optional[str] = None
    @field_validator("timeframes", mode="before")
    def check_enums(cls, values):
        if values is not None:
            if isinstance(values, list[str]):
                timeframes = values
                valid_timeframes = [
                    tf for tf in timeframes if isinstance(tf, LookerTimeFrame)
                ]
                if len(valid_timeframes) < len(timeframes):
                    invalid_timeframes = set(timeframes) - set(valid_timeframes)
                    warnings.warn(
                        f"Invalid timeframes: {invalid_timeframes}. "
                    )
                    values["timeframes"] = valid_timeframes

        return values

class LookerField(LookerViewElement):
    """ with description of each attribute
    """
    field_type: str = Field(default=None, description="The meta-type of the field")

    convert_tz: Optional[bool] = Field(default=None)
    timeframes: Optional[List[LookerTimeFrame]] = Field(default=None)
    can_filter: Optional[Union[bool, str]] = Field(default=None)
    group_item_label: Optional[str] = Field(default=None)
    order_by_field: Optional[str] = Field(default=None)
    suggestable: Optional[bool] = Field(default=None)
    case_sensitive: Optional[bool] = Field(default=None)
    allow_fill: Optional[bool] = Field(default=None)
    required_access_grants: Optional[List[str]] = Field(default=None)
    html: Optional[bool] = Field(default=None)
    tag_append: Optional[List[str]] = None
    description_append: Optional[str] = None
    description_prepend: Optional[str] = None


class Looker(BaseModel):
    """Looker data for a model."""

    dimensions: Optional[List[LookerDimension]] = None