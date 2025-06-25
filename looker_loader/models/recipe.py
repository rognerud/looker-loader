from typing import List, Optional
from pydantic import BaseModel, model_validator
from looker_loader.models.looker import (
    LookerMeasure,
    LookerDimension,
)
from looker_loader.enums import LookerType
from jinja2 import Environment
import re
import logging
# Models for loading recipes, and for generating looker data from the combination of 
# the database and the recipes

def ji2(search, values):
    """Jinja2 render function"""
    jinja_env = Environment()
    target = values.get(search, None)
    if target is None:
        return target
    else:
        pre = preprocess_jinja(target)
        jinjaed = jinja_env.from_string(pre).render(values)
        post = postprocess_jinja(jinjaed)
        logging.debug(f"Jinja2 Rendered {search}: {post}")
        return post

def preprocess_jinja(input_str):
    """ if string contains {{{}}} convert it to { {{}} }"""
    if input_str is not None:
        input_str = input_str.replace("{{{", "{ {{").replace("}}}", "}} }")
        # print(f"Preprocessed Jinja: {input_str}")
    return input_str

def postprocess_jinja(input_str):
    """ if string contains ${ value } convert it to ${value} *any amount of whitespace allowed*"""
    if input_str is not None:
        input_str = re.sub(r'\$\s*\{\s*([^\}]+?)\s*\}', r'${\1}', input_str)
        # print(f"Postprocessed Jinja: {input_str}")
    return input_str

class LookerRecipeDerivedDimension(LookerDimension):
    """A derived dimension in Looker"""
    suffix: str
    remove: Optional[str] = ""
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

        if values.get("sql") is not None:
            values["sql"] = ji2("sql", values)
        if values.get("html") is not None:
            values["html"] =  ji2("html", values)
        if values.get("label") is not None:
            values["label"] = ji2("label", values)
        if values.get("group_label") is not None:
            values["group_label"] = ji2("group_label", values)
        if values.get("description") is not None:
            values["description"] = ji2("description", values)
        if values.get("group_item_label") is None:
            values["group_item_label"] = ji2("group_item_label", values)

        if values.get("sql") is None:
            values["sql"] = f"${{{values.get("parent_name")}}}"
        if values.get("group_label") is None:
            values["group_label"] = values.get("parent_group_label")
        if values.get("description") is None:
            values["description"] = f"{values.get('type')} of {values.get("parent_name")} : {values.get("parent_description")}"
        if values.get("value_format_name") is None:
            values["value_format_name"] = values.get("parent_value_format_name")
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

        def push_down(field : dict, list_params : List[str]):
            for param in list_params:
                field[f"parent_{param}"] = values.get(param)
                if param == "label":
                    field[f"parent_{param}"] = values.get(param) if values.get(param) else values.get("name")
            return field

        if values.get("measures") is not None:
            inherited_children = []
            for child in values.get("measures", []):
                child = push_down(child, ["name", "sql", "type", "group_label", "description", "tags", "value_format_name", "label"])
                inherited_children.append(child)
            values["measures"] = inherited_children

        if values.get("variants") is not None:
            inherited_children = []
            for child in values.get("variants", []):
                child = push_down(child, ["name", "sql", "type", "group_label", "description", "tags", "value_format_name", "label"])
                inherited_children.append(child)
            values["variants"] = inherited_children
        return values

    @model_validator(mode="before")
    def fix_name(cls, values):
        if values.get("suffix") is not None:

            if values.get("sql") is not None:
                values["sql"] = ji2("sql", values)
            if values.get("html") is not None:
                values["html"] = ji2("html", values)
            if values.get("label") is not None:
                values["label"] = ji2("label", values)
            if values.get("group_label") is not None:
                values["group_label"] = ji2("group_label", values)
            if values.get("description") is not None:
                values["description"] = ji2("description", values)
            if values.get("group_item_label") is None:
                values["group_item_label"] = ji2("group_item_label", values)

            values["name"] = f"d_{values.get('parent_name')}_{values.get('suffix')}"
            if values.get("remove") != "" and values.get("remove") is not None:
                values["name"] = values["name"].replace(values.get("remove"), "")
            if values.get("group_label") is None:
                values["group_label"] = values.get("parent_group_label")
            if values.get("description") is None:
                values["description"] = f"derived {values.get('suffix')} of {values.get("parent_name")} : {values.get("parent_description")}"
            if values.get("value_format_name") is None:
                values["value_format_name"] = values.get("parent_value_format_name", "string")
            values["type"] = values.get("parent_type", values.get("type", "string"))
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
    db_type: Optional[str] = None
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
