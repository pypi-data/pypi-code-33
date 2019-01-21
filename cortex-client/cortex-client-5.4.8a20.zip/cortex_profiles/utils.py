import copy
import hashlib
import itertools
import json
import re
import time
import uuid
from collections import OrderedDict, namedtuple, defaultdict
from enum import Enum
from pprint import pprint
from typing import List, Callable, Optional, Any, Tuple, Mapping, Set, Union

import arrow
import attr
import faker
import pandas as pd
import pydash
from pygments import highlight, lexers, formatters
from six import string_types

Function1 = Callable[[object], object]


def attr_fields_except(cls:type, fields_to_ignore: List[attr._make.Attribute]) -> List[attr._make.Attribute]:
    return [attribute for attribute in attr.fields(cls) if attribute not in fields_to_ignore]


def keep_fields_for_attr_value(value:type, fields_to_keep: List[attr._make.Attribute]) -> Mapping[str, Any]:
    return attr.asdict(value, recurse=False, filter=lambda a, v: a in fields_to_keep)


def nest_values_under(d, under):
    return {k: {under: v} for k, v in d.items()}


def append_key_to_values_as(d, key_title):
    return [pydash.merge(value, {key_title: key}) for key, value in d.items()]


def _drop_from_dict(d: dict, skip: List[object]) -> dict:
    if d is None:
        d = None
    if isinstance(d, list):
        return [drop_from_dict(e, skip) for e in d]
    if isinstance(d, dict):
        return {
            k: drop_from_dict(v, skip) for k, v in d.items() if k not in skip
        }
    return d


def drop_from_dict(d: dict, skip: List[object]) -> dict:
    return _drop_from_dict(d, skip)


def modify_named_tuple(nt: namedtuple, modifications:dict) -> namedtuple:
    attr_dict = namedtuple_asdict(nt)
    attr_dict.update(modifications)
    return type(nt)(**attr_dict)


def modify_attr_class(attrClass: type, modifications:dict) -> namedtuple:
    return attr.evolve(attrClass, **modifications)


def utc_timestamp() -> str:
    return str(arrow.utcnow())


def unique_id() -> str:
    return str(uuid.uuid4())


# def flatten_list_recursively(l: list):
#     if not isinstance(l, list):
#         return [l]
#     returnVal = []
#     for x in l:
#         returnVal = returnVal + flatten_list_recursively(x)
#     return returnVal


def flatten_list_recursively(l: Union[List[Any], Any], remove_empty_lists=False):
    if l is None:
        return []
    if not isinstance(l, list):
        return [l]
    # THIS DOES WEIRD STUFF WITH TUPLES!
    return list(itertools.chain(*[flatten_list_recursively(x) for x in l if (not remove_empty_lists or x)]))



def flatmap(listToItterate: List, inputToAppendTo: List, function: Callable) -> List :
    if not listToItterate:
        return []
    head = listToItterate[0]
    tail = listToItterate[1:]
    return flatmap(tail, function(inputToAppendTo, head), function)


def hash_query(query):
    return hashlib.md5("".join(query.lower().split()).encode('utf-8')).hexdigest()


def invert_dict_lookup(d):
    return {v: k for k, v in d.items()}


def value_joiner(inner_df):
    return ",".join(map(lambda x: str(x), inner_df['equity_id'])) if hasattr(inner_df, 'columns') else ",".join(
        map(lambda x: str(x), inner_df))


def pluck(path, d, default={}):
    split_path = [x for x in path.split('.') if x]
    if len(split_path) > 0:
        return pluck('.'.join(split_path[1:]), d.get(split_path[0], default))
    return d


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        return ('%2.2f' % (te - ts), result)

    return timed


def remap_date_formats(date_dict, date_formats, original_format):
    return {
        k: arrow.get(v, original_format).format(date_formats.get(k, original_format))
        for (k, v) in date_dict.items()
    }


def join_inner_arrays(_dict, caster=lambda x: x):
    return {
        k: ",".join(map(caster, v)) if isinstance(v, list) else v
        for (k, v) in _dict.items()
    }


def de_whitespate_dict(_dict):
    return {
        k: v.replace(" ", "") if isinstance(v, str) else v
        for (k, v) in _dict.items()
    }


def pprint_with_header(header, obj):
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(header)
    pprint(obj)
    print("__________________________________________________")
    print("")


def print_json_with_header(header, obj):
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(header)
    print(json_makeup(obj))
    print("__________________________________________________")
    print("")


def print_attr_class_with_header(header, obj):
    if isinstance(obj, list):
        obj = list(map(attr.asdict, obj))
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(header)
    print(json_makeup(attr.asdict(obj)))
    print("__________________________________________________")
    print("")


def print_with_header(header, obj):
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print(header)
    print(obj)
    print("__________________________________________________")
    print("")


def namedtuple_asdict(obj):
    """
    Turns a named tuple into a dict recursively
    From: https://stackoverflow.com/questions/16938456/serializing-a-nested-namedtuple-into-json-with-python-2-7
    """
    if hasattr(obj, "_asdict"): # detect namedtuple
        return OrderedDict(zip(obj._fields, (attr.asdict(item) for item in obj)))
    elif isinstance(obj, string_types): # iterables - strings
        return obj
    elif hasattr(obj, "keys"): # iterables - mapping
        return OrderedDict(zip(obj.keys(), (attr.asdict(item) for item in obj.values())))
    elif hasattr(obj, "__iter__"): # iterables - sequence
        return type(obj)((attr.asdict(item) for item in obj))
    else: # non-iterable cannot contain namedtuples
        return obj


def json_makeup(json_object):
    formatted_json = json.dumps(json_object, sort_keys=True, indent=4)
    colorful_json = highlight(
        formatted_json.encode('UTF-8'),
        lexers.JsonLexer(), formatters.TerminalFormatter()
    )
    return colorful_json


def filter_empty_records(l:List) -> List:
    return [x for x in l if x]


def is_not_none_or_nan(v:object) -> bool:
    return (True if v else False) if not isinstance(v,float) else (not pd.isna(v) if v else False)


def all_values_in_list_are_not_nones_or_nans(l:List) -> bool:
    return all_values_in_list_pass(l, is_not_none_or_nan)


def all_values_in_list_pass(l:List, validity_filter:callable) -> bool:
    return all(map(validity_filter, l))


def tuples_with_nans_to_tuples_with_nones(iter:List[Any]) -> Tuple[Any]:
    # - [x] TODO: Dont like the instance check here ... python has no way of saying "isPrimitive"
        # ... I only want to check for NaNs on primitives... and replace them with None ... not Lists ...
        # Realization: NaNs are floats ...!
    return (
        tuple(map(lambda x: None if isinstance(x, float) and pd.isna(x) else x, list(tup)))
        for tup in iter
    )


def append_to_list(l:List, thing_to_append:Optional[object]) -> List:
    return l + [thing_to_append] if thing_to_append else l


def merge_dicts(a:dict, b:dict) -> dict:
    c = copy.deepcopy(a)
    c.update(b)
    return c


def derive_hour_from_date(iso_timestamp:str):
    d = arrow.get(iso_timestamp)
    return {
        "hour_number": int(d.format("H")),
        "hour": d.format("hhA"),
        "timezone": d.format("ZZ")
    }


def derive_day_from_date(iso_timestamp):
    return str(arrow.get(iso_timestamp).date())


def first_arg_is_type_wrapper(_callable, tuple_of_types):
    return lambda x: x if not isinstance(x, tuple_of_types) else _callable(x)


def field_names_of_attr_class(attr_class:type) -> List[str]:
    return list(map(lambda x: x.name, attr.fields(attr_class)))


# def list_of_dicts_to_list_of_classes(l:List[dict], cls:T) -> List[T]:
#     return list(map(lambda d: cls(**d), l))
# T = TypeVar("T")
# TypeVars and isinstnace does weird stuf ... https://github.com/python/typing/issues/62


def converter_for_list_of_classes(l:List[object], cls) -> List:
    if not l:
        return []

    invalid_types_in_list = list(map(
        lambda x: type(x),
        filter(
            lambda x: not isinstance(x, (cls, dict)),
            l
        )
    ))

    if invalid_types_in_list:
        raise Exception("Invalid type(s) {} in list".format(invalid_types_in_list))

    return list(map(
        lambda y: y if isinstance(y, cls) else cls(**y),
        l
    ))


def union_type_validator(union_type:type) -> Callable[[Any, Any], bool]:
    def validator(self, attribute, value):
        return type(value) in union_type.__args__
    return validator


class AttrsAsDict(object):
    @classmethod
    def keys(cls):
        return list(filter(lambda x: x[0] != "_", cls.__dict__.keys()))

    @classmethod
    def values(cls):
        return [ getattr(cls, k) for k in cls.keys()]

    @classmethod
    def items(cls):
        return dict(zip(cls.keys(), cls.values())).items()



def converter_for_union_type(union_type:type, handlers:Mapping[type, Callable[[Any], Any]]) -> Callable[[Any], Any]:
    def converter(data:Any):
        # Shouldnt assert from union.__args__ ... the union types eats up any types that are subclasses of each other ... such as int and bool ...
        assert type(data) in handlers.keys(), "Value of unexpected type ({}) encountered. Expecting: {}".format(type(data), handlers.keys())
        return handlers[type(data)](data)
    return converter


def converter_for_classes(data:object, desired_attr_type:type, dict_constructor:Optional[Callable[[dict], object]]=None) -> object:
    """
    Convert a attribute into an attr class ...
    :param data:
    :param desired_attr_type:
    :param dict_constructor:
    :return:
    """
    if data is None:
        return None
    if not isinstance(data, (desired_attr_type, dict)):
        raise Exception("Invalid type {} of data.".format(type(data)))
    return data if isinstance(data, desired_attr_type) else (
        desired_attr_type(**data) if not dict_constructor else dict_constructor(data)
    )


def list_converter(l:List[object], desired_attr_type_for_elements:type, item_constructor:Optional[Callable[[dict], object]]=None) -> List[object]:
    if not l:
        return None
    return [
        converter_for_classes(x, desired_attr_type_for_elements, item_constructor) for x in l
    ]


ToYeild = Any


def get_until(
        yielder:Callable[[], Any],
        appender:Callable[[Any, ToYeild], Any],
        ignore_condition:Callable[[Any, ToYeild], bool],
        stop_condition:Callable[[ToYeild], bool],
        to_yield:List) -> ToYeild:
    ignored = 0
    returnVal = to_yield
    while not stop_condition(returnVal):
        next_item = yielder()
        if ignore_condition(next_item, returnVal):
            ignored += 1
        else:
            returnVal = appender(next_item, returnVal)
    # print(ignored, len(returnVal))
    return returnVal


def assign_to_dict(dictionary:dict, key:str, value:object) -> dict:
    return merge_dicts(dictionary, {key: value})


class MappableList(list):

    def map(self, f:Function1) -> 'MappableList':
        return MappableList(map(f, self))

    def filter(self, f:Function1) -> 'MappableList':
        return MappableList(filter(f, self))

    def sort(self, f:Function1) -> 'MappableList':
        return MappableList(sorted(self, key=f))

    @staticmethod
    def from_dict(d:dict) -> 'MappableList':
        return MappableList(d.items())

    @staticmethod
    def from_set(s:set) -> 'MappableList':
        return MappableList(s)

    def to_set(self) -> set:
        return set(self)

    def to_dict(self, value_from_key_function:Function1, dict_instantiator:Callable[[List[Tuple]], dict]=dict) -> dict:
        return dict_instantiator(zip(self, self.map(value_from_key_function)))

    # This can be done with a .map().sum()
    # def sum(self, f:callable):
    #     return sum(self.map(f))


def get_unique_cortex_objects(yielder, limit:int) -> List:
    return list(
        get_until(
            yielder,
            appender=lambda obj, dictionary: assign_to_dict(dictionary, obj["id"], obj),
            ignore_condition=lambda obj, dictionary: obj["id"] in dictionary,
            stop_condition=lambda dictionary: len(dictionary) >= limit,
            to_yield={}
        ).values()
    )


def pick_random_time_between(faker:faker.Generator, start:arrow.Arrow, stop:arrow.Arrow) -> arrow.arrow:
    return arrow.get(faker.date_time_between(start.datetime, stop.datetime))


def seconds_between_times(arrow_time_a:arrow.Arrow, arrow_time_b:arrow.Arrow) -> float:
    return abs(arrow_time_a.float_timestamp - arrow_time_b.float_timestamp)


def reverse_index_dictionary(d:dict) -> dict:
    new_keys = list(set(flatten_list_recursively(list(d.values()))))
    return {
        new_key: [old_key for old_key in list(d.keys()) if new_key in d[old_key]] for new_key in new_keys
    }


def partition_list(l:List, partitions:int) -> List[List]:
    assert partitions >= 1, "Partitions must be >= 1"
    size_of_each_parition = int(len(l) / partitions)
    partitions = zip([x for x in range(0, partitions)], [x for x in range(1, partitions)] + [None])
    return [
        l[start*size_of_each_parition:None if end is None else end*size_of_each_parition]
        for start, end in partitions
    ]


class ValuedObject(object):
    def __init__(self, value):
        self.value = value

class AddableWithObjectsWithValues(object):
    def __add__(self, other):
        if other is None:
            return self
        elif isinstance(other, (ValuedObject, Enum)):
            return ValuedObject(self.value + other.value)
        else:
            raise TypeError("Cannot add {} with {}.".format(type(self), type(other)))

class EnumWithCamelCasedNamesAsDefaultValue(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return pydash.strings.camel_case(name)


class EnumWithNamesAsDefaultValue(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


def merge_enum_values(values:List[Enum], merger:Callable[[list], object]=lambda values: ".".join(values)) -> object:
    return merger(list(map(lambda x: x.value, values)))


def dervie_set_by_element_id(l:List[Any], identifier:Callable[[Any], str]=lambda x: x) -> Set[Any]:
    # from itertools import combinations
    # combinations(l, 2)
    return set({identifier(x): x for x in l}.values())


def group_by_key(l:List[Any], key_deriver:Callable[[Any], str]) -> Mapping[str, List[Any]]:
    returnVal = defaultdict(list)
    for x in l:
        returnVal[key_deriver(x)].append(x)
    return returnVal


def group_objects_by(l:List[Any], group_by:Callable[[Any], str]) -> Mapping[str, List[Any]]:
    unique_groups = set(map(group_by, l))
    return {
        g: list(filter(lambda x: group_by(x) == g, l))
        for g in unique_groups
    }