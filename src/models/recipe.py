from typing import List, Optional
from pydantic import BaseModel, model_validator
from src.models.looker import (
    LookerMeasure,
    LookerDimension,
)

# Models for loading recipes, and for generating looker data from the combination of 
# the database and the recipes

class LookerDerivedDimension(LookerDimension):
    """A derived dimension in Looker"""
    suffix: str
    sql: Optional[str] = None
    html: Optional[str] = None
    measures: Optional[List[LookerMeasure]] = None

    @model_validator(mode="before")
    def fix_name(cls, values):
        values["name"] = f"{values.get('parent_name')}_{values.get('suffix')}"
        values["sql"] = values.get("sql").replace("$X", f"${{{values.get('parent_name')}}}")
        return values

class LookerRecipeDimension(LookerDimension):
    """A recipe dimension in Looker"""
    variants: Optional[List[LookerDerivedDimension]] = None
    measures: Optional[List[LookerMeasure]] = None
    fields: Optional[List[LookerDimension]] = None

    @model_validator(mode="before")
    def create(cls, values):

        def apply(field : dict, list_params : List[str]):
            for param in list_params:
                if field.get(param) is None:
                    field[f"parent_{param}"] = values.get(param)
            return field

        if values.get("measures") is not None:
            inherited_children = []
            for child in values.get("measures", []):
                child = apply(child, ["name","sql","type","group_label", "description", "tags"])
                inherited_children.append(LookerMeasure(**child))
            values["measures"] = inherited_children

        if values.get("variants") is not None:
            inherited_children = []
            for child in values.get("variants", []):
                child = apply(child, ["name","type","group_label", "description", "tags"])
                inherited_children.append(LookerDerivedDimension(**child))
            values["variants"] = inherited_children
        return values

class RecipeFilter(BaseModel):
    """a filter for a recipe"""

    type: Optional[str] = None
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
