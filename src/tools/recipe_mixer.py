
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
        self, filter: RecipeFilter, field_name: str, data_type: str, tags: List[str]
    ) -> bool:
        """
        Check if a filter is relevant for the given field_name, data_type, and tags.
        """
        if filter.data_type and filter.data_type != data_type:
            return False

        if filter.regex_include and not re.search(filter.regex_include, field_name):
            return False

        if filter.regex_exclude and re.search(filter.regex_exclude, field_name):
            return False

        if filter.tags and not any(tag in filter.tags for tag in tags):
            return False

        if filter.fields_include and field_name not in filter.fields_include:
            return False

        if filter.fields_exclude and field_name in filter.fields_exclude:
            return False

        return True

    def create_mixture(
        self, field_name: str, data_type: str, tags: List[str]
    ) -> Optional[Recipe]:
        """
        Combine relevant recipes from cookbook based on field_name, data_type, and tags.
        """
        combined_recipe = None
        # combined_recipe = Recipe()
        if not self.cookbook.recipes:
            raise Exception("No recipes found in cookbook")

        for recipe in self.cookbook.recipes:
            if self.is_filter_relevant(recipe.filters, field_name, data_type, tags):
                # if not combined_recipe.actions:
                # combined_recipe.actions = []
                # if not combined_recipe.measures:
                # combined_recipe.measures = []

                # combined_recipe = self.merge_recipes(combined_recipe, recipe)
                combined_recipe = recipe
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
        self, model_a: DbtModelColumnMeta, model_b: DbtModelColumn
    ) -> DbtModelColumn:
        """Merge the data, with model_b's fields taking precedence"""
        if hasattr(model_b, "meta"):  # and hasattr(model_b.meta.looker,"dimension"):
            merged_meta_data = self._merge_and_replace_empty(
                model_a.model_dump(), model_b.meta.model_dump()
            )
            logging.warning(f"Merged meta model {merged_meta_data}")
            merged_model = DbtModelColumnMeta(**merged_meta_data)
            logging.warning(f"Parsed meta model {merged_model}")
            model_b.meta = merged_model
            logging.warning(f"Merged with model {model_b}")
            return model_b
        else:
            logging.warning(f"Could not merge with model {model_b}")
            return model_b

    def apply_mixture(self, column: DbtModelColumn) -> DbtModelColumn:
        """
        Create a mixture for a column and apply it.
        go through the recipes in the cookbook and apply the relevant ones to the column
        """
        mixture = self.create_mixture(column.name, column.data_type, column.tags)
        if mixture:
            if mixture.actions:
                print("action")
                applied_mixture = DbtModelColumnMeta(
                    **{"looker": {"dimension": mixture.actions}}
                )
                logging.warning(f"Applied mixture {applied_mixture}")
                logging.warning(f"meta {column.meta}")
                modified_column = self._merge_models(applied_mixture, column)
                return modified_column
        return column
