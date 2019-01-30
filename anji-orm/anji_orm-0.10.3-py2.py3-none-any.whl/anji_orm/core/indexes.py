from enum import Enum, auto
import abc
from typing import Dict, Any, TYPE_CHECKING, List, Tuple, Type, TypeVar, Iterator
from itertools import combinations

if TYPE_CHECKING:
    # pylint: disable=unused-import
    from .model import Model

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["IndexPolicy", "IndexPolicySetting", "IndexPolicySettings"]


T = TypeVar('T')


class IndexPolicySetting(Enum):

    only_single_index = auto()
    additional_indexes = auto()


IndexPolicySettings = Dict[IndexPolicySetting, Any]  # pylint: disable=invalid-name


def similar_part_iterator(first: List[T], second: List[T]) -> Iterator[T]:
    """
    Return elements from first, if element not in seconds list stop iteration
    """
    for index, value in enumerate(first):
        if len(second) > index and second[index] == value:
            yield value
        else:
            break


def is_subset(first: List[T], second: List[T], ordered: bool = False) -> bool:
    """
    Check if first list is subset of second
    """
    if not ordered:
        return set(first) <= set(second)
    if len(second) < len(first):
        return False
    for index, value in enumerate(first):
        if second[index] != value:
            return False
    return True


class AbstractIndexPolicy(abc.ABC):

    @abc.abstractmethod
    def build_index_list(self, model: Type['Model']) -> List[Tuple[str, List[str]]]:
        """
        Define a way how to build secondary indexes based on fields that was marked
        as secondary index

        :param secondary_indexes_fields: List of fields that was marked as secondary indexes
        :return: secondary index list
        """

    @abc.abstractmethod
    def select_secondary_index(
            self, model: Type['Model'],
            fields_in_query: List[str], ordered: bool = False) -> Tuple[str, List[str]]:
        """
        Define that way how to select secondary index for query.

        :param secondary_indexes_fields: Fields that used in query
        :return: (selected index, unused elements)
        """

    def extract_secondary_indexes_fields(self, model: Type['Model']) -> List[str]:  # pylint: disable=invalid-name,no-self-use
        return [
            field_name for field_name, field in model._fields.items()
            if field.secondary_index
        ]


class GreedyIndexPolicy(AbstractIndexPolicy):

    """
    Simple index policy based on greedy logic.
    So, that means create index for any field and any field combination.
    For example. model with two indexed fields 'cat' and 'dog' will produce three indexes:
    - cat
    - dog
    - cat:dog
    """

    def build_index_list(self, model: Type['Model']) -> List[Tuple[str, List[str]]]:
        """
        Procude index for every field and any field combinations

        :param secondary_indexes_fields: List of fields that was marked as secondary indexes
        :return: secondary index list
        """
        secondary_indexes_fields = self.extract_secondary_indexes_fields(model)
        secondary_indexes: List[Tuple[str, List[str]]] = []
        secondary_indexes.extend((x, [x]) for x in secondary_indexes_fields)
        secondary_indexes_fields = sorted(secondary_indexes_fields)
        if len(secondary_indexes_fields) > 1:
            for combination_size in range(2, len(secondary_indexes_fields)):
                secondary_indexes.extend(
                    (':'.join(x), list(x)) for x in combinations(secondary_indexes_fields, combination_size)
                )
            secondary_indexes.append((":".join(secondary_indexes_fields), secondary_indexes_fields))
        return secondary_indexes

    def select_secondary_index(
            self, model: Type['Model'],
            fields_in_query: List[str], ordered: bool = False) -> Tuple[str, List[str]]:
        """
        Select index based on all fields or ordered part

        :param secondary_indexes_fields: Fields that used in query
        :return: (selected index, unused elements)
        """
        sorted_fields = sorted(fields_in_query)
        if ordered and sorted_fields != fields_in_query:
            useful_index_part = list(similar_part_iterator(sorted_fields, fields_in_query))
            return ':'.join(useful_index_part), fields_in_query[len(useful_index_part):]
        return ':'.join(sorted_fields), []


class GreedlessIndexPolicy(AbstractIndexPolicy):
    """
    Simple index policy based on greedy logic with filter.
    So, that means create index for any field and any field combination.
    For example. model with two indexed fields 'cat' and 'dog' will produce three indexes:
    - cat
    - dog
    - cat:dog

    But, you can define in configuration list of fields, that will be used only for single index in :code:`only_single_index` key
    """

    def build_index_list(self, model: Type['Model']) -> List[Tuple[str, List[str]]]:
        """
        Procude index for every field and for fields, that not in only_single_index, combinations for fields,

        :param secondary_indexes_fields: List of fields that was marked as secondary indexes
        :return: secondary index list
        """
        secondary_indexes_fields = self.extract_secondary_indexes_fields(model)
        secondary_indexes: List[Tuple[str, List[str]]] = []
        # Create single indexes
        secondary_indexes.extend((x, [x]) for x in secondary_indexes_fields)
        # Create full indexes
        only_single_index_fields = model._index_policy_settings.get(IndexPolicySetting.only_single_index, ())
        full_secondary_index_fields = sorted(x for x in secondary_indexes_fields if x not in only_single_index_fields)
        if len(full_secondary_index_fields) > 1:
            for combination_size in range(2, len(full_secondary_index_fields)):
                secondary_indexes.extend(
                    (':'.join(x), list(x)) for x in combinations(full_secondary_index_fields, combination_size)
                )
            secondary_indexes.append((":".join(full_secondary_index_fields), full_secondary_index_fields))
        return secondary_indexes

    def get_single_field_with_index(self, model: Type['Model'], fields: List[str]) -> Tuple[str, int]:  # pylint: disable=no-self-use
        for only_single_index_field in model._index_policy_settings.get(
                IndexPolicySetting.only_single_index, []):
            if only_single_index_field in fields:
                only_single_index_field_index = fields.index(only_single_index_field)
                if only_single_index_field_index != -1:
                    return only_single_index_field, only_single_index_field_index
        return '', -1

    def select_secondary_index(
            self, model: Type['Model'],
            fields_in_query: List[str], ordered: bool = False) -> Tuple[str, List[str]]:
        """
        Select index based on all fields, if first field not in only_single_index setting

        :param secondary_indexes_fields: Fields that used in query
        :return: (selected index, empty tuple) or (first element, rest tuple)
        """
        sorted_fields = sorted(fields_in_query)
        if ordered:
            if sorted_fields != fields_in_query:
                useful_index_part = list(similar_part_iterator(sorted_fields, fields_in_query))
            else:
                useful_index_part = fields_in_query
            single_field, single_field_index = self.get_single_field_with_index(
                model, useful_index_part
            )
            if single_field_index != -1:
                useful_index_part = useful_index_part[:single_field_index]
            return ':'.join(useful_index_part), fields_in_query[len(useful_index_part):]
        single_field, single_field_index = self.get_single_field_with_index(model, fields_in_query)
        if single_field_index != -1:
            return single_field, [x for x in fields_in_query if x != single_field]
        return ':'.join(sorted_fields), []


class SingleIndexPolicy(AbstractIndexPolicy):

    """
    Simple index policy based on clear logic.
    So, that means create index for any field and no field combination.
    For example. model with two indexed fields 'cat' and 'dog' will produce only two indexes:
    - cat
    - dogs
    """

    def build_index_list(self, model: Type['Model']) -> List[Tuple[str, List[str]]]:
        """
        Procude index for every field and no field combinations

        :param secondary_indexes_fields: List of fields that was marked as secondary indexes
        :return: same as :any:`secondary_indexes_fields` variable
        """
        return [(x, [x]) for x in self.extract_secondary_indexes_fields(model)]

    def select_secondary_index(
            self, model: Type['Model'],
            fields_in_query: List[str], ordered: bool = False) -> Tuple[str, List[str]]:
        """
        Select index based on first fields

        :param secondary_indexes_fields: Fields that used in query
        :return: (first field, rest fields)
        """
        return fields_in_query[0], fields_in_query[1:]


class SingleMoreIndexPolicy(AbstractIndexPolicy):

    def build_index_list(self, model: Type['Model']) -> List[Tuple[str, List[str]]]:
        """
        Procude index for every field and no field combinations

        :param secondary_indexes_fields: List of fields that was marked as secondary indexes
        :return: same as :any:`secondary_indexes_fields` variable
        """
        indexes = [(x, [x]) for x in self.extract_secondary_indexes_fields(model)]
        indexes.extend(model._index_policy_settings.get(IndexPolicySetting.additional_indexes, []))
        return indexes

    def select_secondary_index(
            self, model: Type['Model'],
            fields_in_query: List[str], ordered: bool = False) -> Tuple[str, List[str]]:
        """
        Select index based on first fields

        :param secondary_indexes_fields: Fields that used in query
        :return: (first field, rest fields)
        """
        additional_indexes: List[Tuple[str, List[str]]] = model._index_policy_settings.get(
            IndexPolicySetting.additional_indexes, []
        )
        for index_name, fields_in_index in additional_indexes:
            if is_subset(fields_in_index, fields_in_query, ordered=ordered):
                return index_name, [x for x in fields_in_query if x not in fields_in_index]
        return fields_in_query[0], fields_in_query[1:]


class IndexPolicy(Enum):

    single = SingleIndexPolicy()
    singlemore = SingleMoreIndexPolicy()
    greedyless = GreedlessIndexPolicy()
    greedy = GreedyIndexPolicy()
