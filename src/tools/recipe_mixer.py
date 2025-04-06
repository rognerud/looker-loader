from models.database import DatabaseField, DatabaseTable
from models.recipe import Recipe, CookBook, RecipeFilter
from models.looker import LookerDimension
from typing import List, Optional
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
        if filter.type and filter.type != type:
            return False

        if filter.regex_include and not re.search(filter.regex_include, field.name):
            return False

        if filter.regex_exclude and re.search(filter.regex_exclude, field.name):
            return False

        if filter.tags and not any(tag in filter.tags for tag in field.tags):
            return False

        if filter.fields_include and field.name not in filter.fields_include:
            return False

        if filter.fields_exclude and field.name in filter.fields_exclude:
            return False

        return True

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
                logging.info(f"Found relevant recipe: {recipe.name}")
                combined_recipe = recipe.dimension
        return combined_recipe

    def _merge_and_replace_empty(self, d1, d2):
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

    def combine_dicts(self, dict1, dict2, conflict_resolution="first"):
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

    def apply_mixture(self, column: DatabaseField) -> LookerDimension:
        """
        Create a mixture for a column and apply it.
        go through the recipes in the cookbook and apply the relevant ones to the column
        """
        mixture = self.create_mixture(column)
        if mixture:
            logging.info(f"Applying mixture: {mixture}")
            mixture_ingredients = mixture.model_dump()
            column_ingredients = column.model_dump()
            a = self.combine_dicts(column_ingredients, mixture_ingredients)
            applied_mixture = LookerDimension(
                **a
            )
            # modified_column = self._merge_models(applied_mixture, column)
            return applied_mixture
    
        else:
            logging.warning(f"No mixture found for column {column.name}")
            applied_mixture = LookerDimension(
                **column.model_dump()
            )
            return applied_mixture
