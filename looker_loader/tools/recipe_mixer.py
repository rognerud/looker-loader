from looker_loader.models.database import DatabaseField, DatabaseTable
from looker_loader.models.recipe import LookerMixture, Recipe, CookBook, RecipeFilter, LookerMixtureDimension
from looker_loader.models.config import DatasetConfig
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
    def __init__(self, cookbook: CookBook, lexicanum = None):
        self.cookbook = cookbook
        self.lexicanum = lexicanum

    def is_filter_relevant(
        self, filter: RecipeFilter, field: DatabaseField
    ) -> bool:
        """
        Check if a filter is relevant for the given field_name, type, and tags.
        """
        return all([
            not filter.types or field.type in filter.types,
            not filter.db_types or field.db_type in filter.db_types,
            not filter.regex_include or re.search(filter.regex_include, field.name),
            not filter.regex_exclude or not re.search(filter.regex_exclude, field.name),
            not filter.tags or any(tag in filter.tags for tag in field.tags),
            not filter.fields_include or field.name in filter.fields_include,
            not filter.fields_exclude or field.name not in filter.fields_exclude,
            not filter.field_order or field.order in filter.field_order,
            not filter.is_nested or field.is_nested == filter.is_nested,
            not filter.depth or field.depth in filter.depth,
            not filter.table_regex_include or (field.table_name and re.search(filter.table_regex_include, field.table_name)),
            not filter.table_regex_exclude or (field.table_name and not re.search(filter.table_regex_exclude, field.table_name)),
            not filter.is_clustered or (field.is_clustered and filter.is_clustered) 
        ])

    def create_mixture(
        self, field: DatabaseField, config: DatasetConfig
    ) -> Optional[Recipe]:
        """
        Combine relevant recipes from cookbook based on field_name, type, and tags.
        """
        if not self.cookbook.recipes:
            raise Exception("No recipes found in cookbook")
        if not config:
            raise Exception("No config found")

        relevant_recipes = [
            recipe.dimension.model_dump()
            for recipe in self.cookbook.recipes
            if self.is_filter_relevant(recipe.filters, field)
            and (not config.apply_recipe or recipe.name in config.apply_recipe)
            and (not config.exclude_recipe or recipe.name not in config.exclude_recipe)
        ]

        if self.lexicanum and not config.apply_recipe:
            if field.name in self.lexicanum.root:
                relevant_lexical_entry = self.lexicanum.root[field.name].model_dump()
                if relevant_lexical_entry:
                    relevant_recipes.append(relevant_lexical_entry)

        if not relevant_recipes:
            return None
        else:
            output = self._combine_dicts(
                *relevant_recipes, conflict_resolution="last"
            )
            return output

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
                    if current_dict[key] is None:
                        pass
                    elif isinstance(combined[key], list):
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

    def apply_mixture(self, column: DatabaseField, config: DatasetConfig) -> tuple[LookerMixtureDimension, Optional[List[LookerMixtureDimension]]]:
        """Create and apply a mixture to a column, returning the applied mixture and its variants."""
        
        if not config.unstyled:
            mixture = self.create_mixture(column, config)
        else:
            mixture = None

        if not mixture:
            applied_mixture = LookerMixtureDimension(**column.model_dump())
            return applied_mixture, None

        applied_mixture = LookerMixtureDimension(**
            self._combine_dicts(column.model_dump(), mixture, conflict_resolution="first")
        )

        variants = self._flatten_mixture(applied_mixture)

        return applied_mixture, variants

    def _recursively_apply_mixture(
        self, field: DatabaseField, config: DatasetConfig
    ) -> list[LookerMixtureDimension]:
        """
        Recursively apply the mixture to the column and its subfields.
        """
        d, v = self.apply_mixture(field, config) 

        if field.fields:
            d.fields = []
            for f in field.fields:
                r = self._recursively_apply_mixture(f, config)
                d.fields.extend(r)

        result = [d]
        if isinstance(v, list):
            result.extend(v)
        elif isinstance(v, LookerMixtureDimension):
            result.append(v)
        return result

    def mixturize(self, table: DatabaseTable, config: DatasetConfig) -> LookerMixture:
        """
        Search for and apply recipes to the table.
        """
        if not table.fields:
            raise Exception("No fields found in table")

        fields = []
        for field in table.fields:
            applied = self._recursively_apply_mixture(field, config)
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