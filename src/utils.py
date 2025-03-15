import logging
from src.exceptions import CliError
import json
import yaml

class FileHandler:
    def read(self, file_path: str, file_type="json") -> dict:
        """Load file from disk. Default is to load as a JSON file

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing the JSON data OR raw contents
        """
        try:
            with open(file_path, "r") as f:
                if file_type == "json":
                    raw_file = json.load(f)
                elif file_type == "yaml":
                    raw_file = yaml.safe_load(f)
                else:
                    raw_file = f.read()
        except FileNotFoundError as e:
            logging.error(
                f"Could not find file at {file_path}. Use --target-dir to change the search path for the manifest.json file."
            )
            raise CliError("File not found") from e

        return raw_file

    def write(self, file_path: str, contents: str):
        """Write contents to a file

        Args:
            file_path (str): _description_
            contents (str): _description_

        Raises:
            CLIError: _description_
        """
        try:
            with open(file_path, "w") as f:
                f.truncate()  # Clear file to allow overwriting
                f.write(contents)
        except Exception as e:
            logging.error(f"Could not write file at {file_path}.")
            raise CliError("Could not write file") from e


class StructureGenerator:
    """Split columns into groups for views and joins"""

    def __init__(self, args):
        self._cli_args = args

    def _find_levels(self, model: DbtModel) -> dict:
        """
        Return group keys for the model columns by detecting array columns
        and grouping them in the correct depth level
        """
        grouped_data = {(0, ""): []}

        for column in model.columns.values():
            depth = column.name.count(".") + 1
            prepath = column.name

            key = (depth, prepath)

            if column.data_type == "ARRAY":
                if key not in grouped_data:
                    grouped_data[key] = []

        return grouped_data

    def _find_permutations(self, column_name: str) -> list:
        """Return a sorted list of permutation keys for a column name
        a permutation key is a tuple with the depth level and the column name
        for example:
        column_name = "a.b.c"
        permutations = [
            (3, "a.b.c"),
            (2, "a.b"),
            (1, "a"),
            (0, "")
        ]
        """
        keys = []
        path_parts = column_name.split(".")
        permutations = [
            ".".join(path_parts[: i + 1]) for i in range(len(path_parts) - 1, -1, -1)
        ]
        permutations.append("")
        for perm in permutations:
            if perm == "":
                current_depth = 0
            else:
                current_depth = perm.count(".") + 1
            key = (current_depth, perm)
            keys.append(key)

        sorted_keys = sorted(keys, key=lambda x: x[0], reverse=True)
        return sorted_keys

    def process_model(self, model: DbtModel):
        """analyze the model to group columns for views and joins"""

        grouped_data = self._find_levels(model)

        for column in model.columns.values():
            permutations = self._find_permutations(column.name)

            matched = False
            if permutations:
                for permutation_key in permutations:
                    if not matched and permutation_key in grouped_data.keys():
                        matched = True
                        # Add arrays as columns in two depth levels
                        if column.data_type == "ARRAY":
                            if permutation_key[1] == column.name:
                                matched = False

                                if len(column.inner_types) == 1:
                                    column_copy = column.model_copy()
                                    column_copy.is_inner_array_representation = True
                                    column_copy.data_type = column.inner_types[0]
                                    grouped_data[permutation_key].append(column_copy)

                        if matched:
                            grouped_data[permutation_key].append(column)

            if not matched:
                raise Exception(f"Could not find a match for column {column.name}")
        return grouped_data


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
