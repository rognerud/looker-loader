# class StructureGenerator:
#     """Split columns into groups for views and joins"""

#     def __init__(self, args):
#         self._cli_args = args

#     def _find_levels(self, model: DbtModel) -> dict:
#         """
#         Return group keys for the model columns by detecting array columns
#         and grouping them in the correct depth level
#         """
#         grouped_data = {(0, ""): []}

#         for column in model.columns.values():
#             depth = column.name.count(".") + 1
#             prepath = column.name

#             key = (depth, prepath)

#             if column.data_type == "ARRAY":
#                 if key not in grouped_data:
#                     grouped_data[key] = []

#         return grouped_data

#     def _find_permutations(self, column_name: str) -> list:
#         """Return a sorted list of permutation keys for a column name
#         a permutation key is a tuple with the depth level and the column name
#         for example:
#         column_name = "a.b.c"
#         permutations = [
#             (3, "a.b.c"),
#             (2, "a.b"),
#             (1, "a"),
#             (0, "")
#         ]
#         """
#         keys = []
#         path_parts = column_name.split(".")
#         permutations = [
#             ".".join(path_parts[: i + 1]) for i in range(len(path_parts) - 1, -1, -1)
#         ]
#         permutations.append("")
#         for perm in permutations:
#             if perm == "":
#                 current_depth = 0
#             else:
#                 current_depth = perm.count(".") + 1
#             key = (current_depth, perm)
#             keys.append(key)

#         sorted_keys = sorted(keys, key=lambda x: x[0], reverse=True)
#         return sorted_keys

#     def process_model(self, model: DbtModel):
#         """analyze the model to group columns for views and joins"""

#         grouped_data = self._find_levels(model)

#         for column in model.columns.values():
#             permutations = self._find_permutations(column.name)

#             matched = False
#             if permutations:
#                 for permutation_key in permutations:
#                     if not matched and permutation_key in grouped_data.keys():
#                         matched = True
#                         # Add arrays as columns in two depth levels
#                         if column.data_type == "ARRAY":
#                             if permutation_key[1] == column.name:
#                                 matched = False

#                                 if len(column.inner_types) == 1:
#                                     column_copy = column.model_copy()
#                                     column_copy.is_inner_array_representation = True
#                                     column_copy.data_type = column.inner_types[0]
#                                     grouped_data[permutation_key].append(column_copy)

#                         if matched:
#                             grouped_data[permutation_key].append(column)

#             if not matched:
#                 raise Exception(f"Could not find a match for column {column.name}")
#         return grouped_data
