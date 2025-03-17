from typing import List, Optional
from pydantic import BaseModel, model_validator
from src.models.looker import (
    LookerMeasure,
    LookerDimension,
)

class LookerDerivedDimension(LookerDimension):
    """A derived dimension in Looker"""
    prefix: Optional[str] = None
    # $x is a placeholder for the field name
    sql: Optional[str] = None
    # $x is a placeholder for the field name
    html: Optional[str] = None

class LookerRecipeDimension(LookerDimension):
    """A recipe dimension in Looker"""
    variants: Optional[List[LookerDerivedDimension]] = None

class RecipeFilter(BaseModel):
    """a filter for a recipe"""

    data_type: Optional[str] = None
    regex_include: Optional[str] = None
    regex_exclude: Optional[str] = None
    tags: Optional[List[str]] = None
    fields_include: Optional[List[str]] = None
    fields_exclude: Optional[List[str]] = None

    @model_validator(mode="before")
    def check_at_least_one_field(cls, values):
        # Check if all values are None
        if all(value is None for value in values.values()):
            raise ValueError("At least one field must be specified.")
        return values


class Recipe(BaseModel):
    """
    A recipe for what to generate automatically in Looker
    - filters: filter what columns to apply the recipe to
    - dimension: metadata to add on the column
    - measures: measures to generate for the columns
    that are useful for that data
    """

    name: str
    filters: RecipeFilter
    dimension: Optional[LookerRecipeDimension] = None


class CookBook(BaseModel):
    """A cookbook of recipes"""

    # every recipe has a name
    recipes: List[Recipe]
