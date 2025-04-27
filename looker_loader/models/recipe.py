from typing import List, Optional
from pydantic import BaseModel, model_validator
from looker_loader.models.looker import (
    LookerMeasure,
    LookerDimension,
)
from looker_loader.enums import LookerType

# Models for loading recipes, and for generating looker data from the combination of 
# the database and the recipes

class LookerRecipeDerivedDimension(LookerDimension):
    """A derived dimension in Looker"""
    suffix: str
    sql: Optional[str] = None
    html: Optional[str] = None
    measures: Optional[List[LookerMeasure]] = None
    variants: Optional[List['LookerRecipeDerivedDimension']] = None

class LookerRecipeDimension(LookerDimension):
    """A recipe dimension in Looker"""
    variants: Optional[List[LookerRecipeDerivedDimension]] = None
    measures: Optional[List[LookerMeasure]] = None
    fields: Optional[List[LookerDimension]] = None

class LookerMixtureMeasure(LookerMeasure):
    """A derived measure in Looker"""
    name: str
    sql: str
    html: Optional[str] = None

    @model_validator(mode="before")
    def fix_name(cls, values):
        values["name"] = f"m_{values.get('type')}_{values.get('parent_name')}"
        if values.get("sql") is None:
            values["sql"] = f"${{{values.get("parent_name")}}}"
        if values.get("group_label") is None:
            values["group_label"] = values.get("parent_group_label")
        if values.get("description") is None:
            values["description"] = f"{values.get('type')} of {values.get("parent_name")} : {values.get("parent_description")}"
        return values

class LookerMixtureDimension(LookerRecipeDimension):
    measures: Optional[List[LookerMixtureMeasure]] = None
    variants: Optional[List['LookerMixtureDimension']] = None
    fields: Optional[List['LookerMixtureDimension']] = None
    suffix: Optional[str] = None
    is_variant: Optional[bool] = None
    sql_table_name: Optional[str] = None

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
                child = apply(child, ["name", "sql", "type", "group_label", "description", "tags"])
                inherited_children.append(child)
            values["measures"] = inherited_children

        if values.get("variants") is not None:
            inherited_children = []
            for child in values.get("variants", []):
                child = apply(child, ["name", "sql", "type", "group_label", "description", "tags"])
                inherited_children.append(child)
            values["variants"] = inherited_children
        return values

    @model_validator(mode="before")
    def fix_name(cls, values):
        if values.get("suffix") is not None:
            values["name"] = f"d_{values.get('parent_name')}_{values.get('suffix')}"
            if values.get("group_label") is None:
                values["group_label"] = values.get("parent_group_label")
            if values.get("description") is None:
                values["description"] = f"derived {values.get('suffix')} of {values.get("parent_name")} : {values.get("parent_description")}"
            values["type"] = values.get("parent_type", "string")
            values["sql"] = values.get("sql").replace("$x", f"${{{values.get('parent_name')}}}")
        return values

class LookerMixture(BaseModel):
    """A mixture of dimensions and measures in Looker"""
    name: str
    fields: Optional[List[LookerMixtureDimension]] = None
    measures: Optional[List[LookerMixtureMeasure]] = None
    dimensions: Optional[List[LookerMixtureDimension]] = None
    sql: Optional[str] = None
    sql_table_name: Optional[str] = None

class RecipeFilter(BaseModel):
    """a filter for a recipe"""

    type: Optional[LookerType] = None
    regex_include: Optional[str] = None
    regex_exclude: Optional[str] = None
    tags: Optional[List[str]] = None
    fields_include: Optional[List[str]] = None
    fields_exclude: Optional[List[str]] = None
    field_order: Optional[List[int]] = None

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
