# -*- coding: utf-8 -*-

"""
Perform a grid search over all the parameters in the list.
"""

from typing import List, Union

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


def grid_search(config: dict) -> List[dict]:
    """
    Performs a grid search over all the elements of the config.
    Args:
        config (dict): A map of all the keys to use, to a list of values to search through.
    Returns:
        A list (superset) of all possible configuration permutations.
    """
    data_list = [{}]
    for k, v in config.items():
        data_list = recursive_append(data_list, k, v)
    return data_list


def recursive_append(
        data_list: List[dict],
        field_name: str,
        field_value: Union[list, str, int, float]):
    """ Duplicate all fields in the inbound data list and create a copy for each value. """

    # Master List.
    master_data_list: List[dict] = []

    # Duplicate the data in the list.
    for data in data_list:

        new_data = {k: v for k, v in data.items()}

        # For each data, create a copy and append the value.
        if type(field_value) is list:  # If it is a list.
            for vi in field_value:
                # Copy it AGAIN.
                sub_data = {k: v for k, v in new_data.items()}
                sub_data[field_name] = vi
                master_data_list.append(sub_data)
        else:  # Not a list?
            new_data[field_name] = field_value
            master_data_list.append(new_data)

    return master_data_list
