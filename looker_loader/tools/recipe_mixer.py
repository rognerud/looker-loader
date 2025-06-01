from looker_loader.models.database import DatabaseField, DatabaseTable
from looker_loader.models.recipe import LookerMixture, Recipe, CookBook, RecipeFilter, LookerRecipeDimension, LookerRecipeDerivedDimension, LookerMixtureDimension

from typing import List, Optional, Union
import re
import logging

def extend_unique_dicts_tuple(existing_list, new_items):
    """Extends a list with only unique dictionaries (represented as tuples of sorted items)."""
    existing_set = {tuple(sorted(d.items())) for d in existing_list}  # Convert existing dicts to tuples
    for item in new_items:
        tuple_item = tuple(sorted(item.items()))
        if tuple_item not in existing_set:
            existing_list.append(item)
            existing_set.add(tuple_item)


def remove_nones(data):
    """Recursively removes None values from dictionaries and lists."""
    if isinstance(data, dict):
        return {k: remove_nones(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_nones(item) for item in data if item is not None]
    else:
        return data  # Return non-None values as is

class RecipeMixer:
    def __init__(self, cookbook: CookBook):
        self.cookbook = cookbook

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
        if not self.cookbook.recipes:
            raise Exception("No recipes found in cookbook")

        relevant_recipes = [
            recipe.dimension.model_dump() for recipe in self.cookbook.recipes
            if self.is_filter_relevant(recipe.filters, field)
        ]
        if not relevant_recipes:
            return None
        else:
            output = self._combine_dicts(
                *relevant_recipes, conflict_resolution="last"
            )
            return output

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

    def _combine_dicts(self, *args, conflict_resolution="first"):
        """
        Combines an arbitrary number of dictionaries, handling key conflicts
        based on the chosen strategy and the order of the dictionaries.
        Args:
            *dicts: An arbitrary number of dictionaries to combine.
            conflict_resolution: How to handle keys present in multiple dictionaries:
                - "first" (default): Keep the value from the first dictionary
                                    where the key appears.
                - "last": Keep the value from the last dictionary where the key appears.
                - "append": If values are lists, append the new value to the existing list.
                            If the existing value is not a list, it will be converted to a list
                            containing the original value before appending the new value.
                            If the new value is a list, it will be extended to the original list.
                - "custom": Uses a custom function to resolve conflicts. The function
                            should accept the key and a list of values (in order of
                            appearance in the dictionaries) and return the resolved value.
        Returns:
            A new dictionary containing the combined keys and values.
        """
        logging.debug("----- Combining dictionaries -----")
        if len(args) == 1 and isinstance(args[0], list):
            # If the only argument is a list, treat it as a list of dictionaries
            logging.debug("Received a list of dictionaries as the second argument.")
            predicts = args[0]
        else:
            logging.debug("Received multiple dictionaries as arguments.")
            # Otherwise, treat all arguments as individual dictionaries
            predicts = args[0:]

        if not predicts:
            logging.debug("No dictionaries provided to combine.")
            return {}  # Handles the case where an empty list was passed in.

        if len(predicts) == 1:
            logging.debug("Only one dictionary provided, returning it as is.")
            # If only one dictionary is provided, return it as is, but not as a tuple.
            return predicts[0]

        combined = predicts[0]  # Start with the first dictionary
        dicts = predicts[1:]  # Remaining dictionaries to process

        for current_dict in dicts:
            for key, value in current_dict.items():
                if key in combined:
                    if combined[key] is None:
                        pass
                    if isinstance(combined[key], list):
                        if isinstance(value, list):
                            if len(value) > 0:
                                extend_unique_dicts_tuple(combined[key], value)
                        elif isinstance(value, dict):
                            tuple_value = tuple(sorted(value.items()))
                            existing_set = {tuple(sorted(d.items())) for d in combined[key]}
                            if tuple_value not in existing_set:
                                combined[key].append(value)
                        else:
                            if value not in combined[key] and value is not None:
                                combined[key].append(value)
                    else:
                        if conflict_resolution == "first":
                            pass  # Keep the first value (already in `combined`)
                        elif conflict_resolution == "last":
                            combined[key] = value  # Override with the last value
                else:
                    combined[key] = value  # Key not in combined, add it

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

        combined_data = self._combine_dicts(column.model_dump(), mixture, conflict_resolution="first")
        logging.info(column)
        logging.info(remove_nones(mixture))
        logging.info(remove_nones(combined_data))
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