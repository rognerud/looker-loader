from looker_loader.models.database import DatabaseField, DatabaseTable
from looker_loader.models.recipe import LookerMixture, Recipe, CookBook, RecipeFilter, LookerRecipeDimension, LookerRecipeDerivedDimension, LookerMixtureDimension

from typing import List, Optional, Union
import re
import logging

class RecipeMixer:
    def __init__(self, cookbook: CookBook):
        self.cookbook = cookbook

    def merge_recipes(self, base: Recipe, override: Recipe) -> Recipe:
        """
        Merge two Recipe objects, with override having priority over base.
        """
        if override.name and base.name:
            base.name = f"{base.name} - {override.name}"

        # if override.actions:
        #     base.actions = base.actions or []
        #     base.actions.extend(override.actions)

        # if override.measures:
        #     base.measures = base.measures or []
        #     base.measures.extend(override.measures)

        return base

    def is_filter_relevant(
        self, filter: RecipeFilter, field: DatabaseField
    ) -> bool:
        """
        Check if a filter is relevant for the given field_name, type, and tags.
        """
        return all([
            not filter.type or filter.type == field.type,
            not filter.regex_include or re.search(filter.regex_include, field.name),
            not filter.regex_exclude or not re.search(filter.regex_exclude, field.name),
            not filter.tags or any(tag in filter.tags for tag in field.tags),
            not filter.fields_include or field.name in filter.fields_include,
            not filter.fields_exclude or field.name not in filter.fields_exclude,
            not filter.field_order or field.order in filter.field_order,
        ])

    def create_mixture(
        self, field: DatabaseField
    ) -> Optional[Recipe]:
        """
        Combine relevant recipes from cookbook based on field_name, type, and tags.
        """
        combined_recipe = None
        # combined_recipe = Recipe()
        if not self.cookbook.recipes:
            raise Exception("No recipes found in cookbook")

        for recipe in self.cookbook.recipes:
            if self.is_filter_relevant(recipe.filters, field):
                # if not combined_recipe.actions:
                # combined_recipe.actions = []
                # if not combined_recipe.measures:
                # combined_recipe.measures = []
                # combined_recipe = self.merge_recipes(combined_recipe, recipe)
                logging.debug(f"Found relevant recipe: {recipe.name} for field {field.name}")
                combined_recipe = recipe.dimension
        return combined_recipe

    def _merge_and_replace_empty(self, d1, d2):
        """
        Merge two dictionaries, replacing empty values in d1 with values from d2.
        """
        merged = {}

        def is_empty(value):
            # Define what you consider as "empty"
            return value in [None, "", [], {}, set(), tuple()]

        for key in set(d1) | set(d2):
            value1 = d1.get(key)
            value2 = d2.get(key)

            if isinstance(value1, dict) and isinstance(value2, dict):
                merged[key] = self._merge_and_replace_empty(value1, value2)
            elif isinstance(value1, dict):
                merged[key] = self._merge_and_replace_empty(value1, {})
            elif isinstance(value2, dict):
                merged[key] = self._merge_and_replace_empty({}, value2)
            elif is_empty(value2):
                merged[key] = value1
            else:
                merged[key] = value2

        # Remove keys with None values
        merged = {k: v for k, v in merged.items() if v is not None}

        return merged

    def _merge_models(
        self, model_a: DatabaseField, model_b: DatabaseField
    ) -> DatabaseField:
        """Merge the data, with model_b's fields taking precedence"""
        if hasattr(model_b, "meta"):  # and hasattr(model_b.meta.looker,"dimension"):
            merged_meta_data = self._merge_and_replace_empty(
                model_a.model_dump(), model_b.meta.model_dump()
            )
            logging.warning(f"Merged meta model {merged_meta_data}")
            merged_model = DatabaseField(**merged_meta_data)
            logging.warning(f"Parsed meta model {merged_model}")
            model_b.meta = merged_model
            logging.warning(f"Merged with model {model_b}")
            return model_b
        else:
            logging.warning(f"Could not merge with model {model_b}")
            return model_b

    def _combine_dicts(self, dict1, dict2, conflict_resolution="first"):
        """
        Combines two dictionaries, handling key conflicts based on the chosen strategy.

        Args:
            dict1: The first dictionary.
            dict2: The second dictionary.
            conflict_resolution:  How to handle keys present in both dictionaries:
            - "first": Keep the value from dict1.
            - "second" (default): Keep the value from dict2.
            - "merge":  If values are lists, merge them.  Otherwise, raise ValueError.

        Returns:
            A new dictionary containing the combined keys and values.
        """

        combined = dict1.copy()  # Start with a copy of dict1

        for key, value in dict2.items():
            if key in combined:
                if conflict_resolution == "first":
                    pass  # Keep the value from dict1 (already in combined)
                elif conflict_resolution == "second":
                    combined[key] = value # Override with value from dict2
                elif conflict_resolution == "merge":
                    if isinstance(combined[key], list) and isinstance(value, list):
                        combined[key] = combined[key] + value  # Merge the lists
                    else:
                        raise ValueError(f"Cannot merge non-list values for key '{key}'.")
                else:
                    raise ValueError(f"Invalid conflict_resolution: {conflict_resolution}")
            else:
                combined[key] = value  # Key only in dict2, add it

        return combined

    def _flatten_mixture(self, mixture: LookerMixtureDimension) -> list[LookerMixtureDimension]:
        """
        Flatten the mixture into dimensions and measures.
        """

        def recurse_variants(mixture, dimensions = None):
            if dimensions is None:
                dimensions = []

            if mixture.variants:
                for variant in mixture.variants:
                    dimensions.append(variant)
                    if variant.variants:
                        var_dimensions = recurse_variants(variant)
                        dimensions.extend(var_dimensions)
            return dimensions

        mixture = recurse_variants(mixture)

        return mixture

    def apply_mixture(self, column: DatabaseField) -> tuple[LookerMixtureDimension, Optional[List[LookerMixtureDimension]]]:
        """Create and apply a mixture to a column, returning the applied mixture and its variants."""
        mixture = self.create_mixture(column)

        if not mixture:
            logging.debug(f"No mixture found for column {column.name}")
            applied_mixture = LookerMixtureDimension(**column.model_dump())
            return applied_mixture, None

        combined_data = self._combine_dicts(column.model_dump(), mixture.model_dump())
        applied_mixture = LookerMixtureDimension(**combined_data)
        variants = self._flatten_mixture(applied_mixture)

        return applied_mixture, variants

    def _recursively_apply_mixture(
        self, field: DatabaseField
    ) -> list[LookerMixtureDimension]:
        """
        Recursively apply the mixture to the column and its subfields.
        """
        d, v = self.apply_mixture(field) 

        if field.fields:
            d.fields = []
            for f in field.fields:
                r = self._recursively_apply_mixture(f)
                if len(r) > 1:
                    logging.info(r)
                d.fields.extend(r)

        result = [d]
        if isinstance(v, list):
            result.extend(v)
        elif isinstance(v, LookerMixtureDimension):
            result.append(v)
        return result

    def mixturize(self, table: DatabaseTable) -> DatabaseTable:
        """
        Search for and apply recipes to the table.
        """
        if not table.fields:
            raise Exception("No fields found in table")

        fields = []
        for field in table.fields:
            applied = self._recursively_apply_mixture(field)
            if isinstance(applied, list):
                fields.extend(applied)
            else:
                fields.append(applied)

        model = LookerMixture(**{
            "name": table.name,
            "sql_table_name": table.sql_table_name,
            "fields": fields,
        })

        return model