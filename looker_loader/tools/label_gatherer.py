from looker_loader.models.recipe import LookerMixture, LookerMixtureDimension
from typing import List, Set
import json
import Levenshtein
def gather_field_names(mixtures: List[LookerMixture]) -> Set[str]:
    """
    Gather field names from Looker mixtures and their dimensions.
    """
    field_names = []
    
    for mixture in mixtures:
        for dimension in mixture.fields:
            field_names.append(dimension.name)

            if dimension.measures is not None:
                for measure in dimension.measures:
                    field_names.append(measure.name)
        

    return set(field_names)

def group_strings_by_similarity(string_list, group_size=10, similarity_threshold=0.8):
    """
    Groups strings into clusters of similar strings based on Levenshtein distance.

    Args:
        string_list: A list of strings.
        group_size: The desired size of each group.
        similarity_threshold: A threshold for similarity (0.0 to 1.0). Higher = more similar.
                              This is a percentage, calculated as (max_distance - distance) / max_distance

    Returns:
        A list of lists, where each inner list is a group of similar strings.
    """

    groups = []
    unassigned = list(string_list)  # Copy of the list to track unassigned strings

    while unassigned:
        # Start a new group with the first unassigned string
        group = [unassigned.pop(0)]  # Remove and take the first element

        # Find the most similar strings to the first string in the group and add them
        while len(group) < group_size and unassigned:
            best_match = None
            best_similarity = 0

            for i, s in enumerate(unassigned):
                distance = Levenshtein.distance(group[0], s)
                max_distance = max(len(group[0]), len(s))  # Normalize by length
                similarity = (max_distance - distance) / max_distance  # Calculate similarity as a percentage

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = i

            if best_match is not None and best_similarity >= similarity_threshold:
                group.append(unassigned.pop(best_match))
            else:
                break  # No more good matches found

        groups.append(group)

    return groups