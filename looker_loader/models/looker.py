from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError
import warnings
from looker_loader.enums import LookerType, LookerDateTimeframes, LookerTimeTimeframes

from looker_loader.enums import (
    LookerType,
    LookerMeasureType,
    LookerTimeFrame,
    LookerValueFormatName,
)

#  metaclass
class LookerViewElement(BaseModel):
    """Looker data for a view element."""
    name: str = Field(default=None)
    type: Optional[Literal[
        "bin",
        "date",
        "datetime",
        "distance",
        "duration",
        "location",
        "number",
        "string",
        "tier",
        "time",
        "yesno",
        "zipcode",
        "timestamp",
        None
    ]] = None
    label: Optional[str] = None
    hidden: Optional[bool] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

    value_format_name: Optional[str] = Field(default=None)
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

    # Fields specific to certain measure types
    approximate: Optional[bool] = None  # For count_distinct
    approximate_threshold: Optional[int] = None  # For count_distinct
    precision: Optional[int] = None  # For average, sum
    sql_distinct_key: Optional[str] = None  # For count_distinct
    percentile: Optional[int] = None  # For percentile measures
    required_access_grants: Optional[List[str]] = Field(default=None)
    filters: Optional[List[LookerMeasureFilter]] = None
    sql: Optional[str] = None  # SQL expression for the measure

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
    primary_key: Optional[Union[bool, str]] = Field(default=None)
    convert_tz: Optional[Union[str, bool]] = Field(default=None)
    timeframes: Optional[List[str]] = Field(default=None)
    can_filter: Optional[Union[bool, str]] = Field(default=None)
    group_item_label: Optional[str] = Field(default=None)
    order_by_field: Optional[str] = Field(default=None)
    suggestable: Optional[bool] = Field(default=None)
    case_sensitive: Optional[bool] = Field(default=None)
    allow_fill: Optional[bool] = Field(default=None)
    required_access_grants: Optional[List[str]] = Field(default=None)
    html: Optional[str] = Field(default=None)
    sql: Optional[str] = None
    # fields: Optional[List['LookerDimension']] = None


    # @field_validator("timeframes", mode="before")
    # def check_enums(cls, values):
    #     if values is not None:
    #         if isinstance(values, list[str]):
    #             timeframes = values
    #             valid_timeframes = [
    #                 tf for tf in timeframes if isinstance(tf, LookerTimeFrame)
    #             ]
    #             if len(valid_timeframes) < len(timeframes):
    #                 invalid_timeframes = set(timeframes) - set(valid_timeframes)
    #                 warnings.warn(
    #                     f"Invalid timeframes: {invalid_timeframes}. "
    #                 )
    #                 values["timeframes"] = valid_timeframes

    #     return values


class ValidatedLookerDimension(LookerDimension):
    """Looker data for a dimension with validation."""

    @field_validator("convert_tz", "hidden", "primary_key", mode="after")
    @classmethod
    def bool_to_yesno(cls, value):
        if isinstance(value, bool):
            if value:
                return "yes"
            else:
                return "no"
        return value

class ValidatedLookerDimensionGroup(LookerDimension):
    """Looker data for a dimension group with validation."""

    @model_validator(mode="before")
    def convert_to_dimension_group(cls, values):
        if values.get("type") in (
            "date",
            "time"
        ):
            # Convert to dimension group
            values["type"] = "time"
            values["timeframes"] = LookerDateTimeframes.str_values()
            values["convert_tz"] = False

        elif values.get("type") in (
            "datetime",
            "timestamp",
        ):
            # Convert to dimension group
            values["type"] = "time"
            values["timeframes"] = LookerTimeTimeframes.str_values()
            values["convert_tz"] = True

        return values

    @field_validator("convert_tz", "hidden", mode="after")
    @classmethod
    def bool_to_yesno(cls, value):
        if isinstance(value, bool):
            if value:
                return "yes"
            else:
                return "no"
        return value

class LookerView(BaseModel):
    """Looker data for a view."""

    name: str
    label: Optional[str] = None
    sql_table_name: Optional[str] = None

    dimensions: Optional[List[ValidatedLookerDimension]] = Field(default=None)
    dimension_groups: Optional[List[ValidatedLookerDimensionGroup]] = Field(default=None)
    measures: Optional[List[LookerMeasure]] = Field(default=None)

    @model_validator(mode="before")
    def handle_time_and_dates(cls, values):
        """Convert time and date dimensions to dimension groups."""
        if values.get("dimensions"):
            dimensions = []
            dimensions_groups = []

            for dimension in values["dimensions"]:
                if dimension.get("type") in (
                    "date",
                    "datetime",
                    "timestamp",
                    "time",
                ):
                    dimensions_groups.append(dimension)
                else:
                    dimensions.append(dimension)
            values["dimensions"] = dimensions
            values["dimension_groups"] = dimensions_groups
        return values
