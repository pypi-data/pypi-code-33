import re
from typing import Union

from cytoolz.curried import curry, assoc, keyfilter, get_in
from glom import glom
from glom.core import PathAccessError

from genomoncology.parse.doctypes import DocType
from gosdk.logger import get_logger


@curry
def transform(glom_spec: Union[dict, str], value: dict):
    # e.g.: transform(call, {"AN_EAS": "annotations.GNOMAD__AN_EAS__mint.0"})
    if value:
        try:
            transformed = glom(value, glom_spec)
            return transformed

        except PathAccessError as e:
            get_logger().warn("transform (path error)", e=e)
            pass


@curry
def filter_keys(whitelist, value):
    return keyfilter(lambda k: k in whitelist, value)


@curry
def get_in_field(field_name, value):
    field_name = field_name.split(".")
    return get_in(field_name, value)


@curry
def rename(old_name, new_name, value):
    return assoc(value, new_name, get_in_field(old_name, value))


@curry
def filter_private_keys(value):
    return keyfilter(lambda k: not k.startswith("__"), value)


MULTI_FIELD = re.compile("^.*__m(string|float|int)$")
DELS = re.compile("[|:;,]")


def dot_to_none(v):
    if v != ".":
        return v


def split_value(field_value):
    if isinstance(field_value, str):
        field_value = [dot_to_none(v) for v in DELS.split(field_value)]
    return field_value


def is_multi_field(field_name):
    return MULTI_FIELD.fullmatch(field_name)


@curry
def name_mapping(mapping, value, empty_values=(None,), check_multi=True):
    new_dict = {}
    for (new_name, old_name) in mapping.items():
        field_value = get_in_field(old_name, value)

        # add __record__
        if old_name == "__record__":
            new_dict = assoc(new_dict, new_name, field_value)
            continue

        if field_value not in empty_values:
            if check_multi and is_multi_field(new_name):
                field_value = split_value(field_value)

            new_dict = assoc(new_dict, new_name, field_value)

    return new_dict


@curry
def add_flag(bed_filter, flag_name, value):
    if not DocType.HEADER.is_a(value):
        item = (value.get("chr"), value.get("start"))

        bed_value_list = []
        is_present = False
        for i in bed_filter.search(item):
            bed_value_list += i.data
            is_present = True

        if bed_value_list:
            value = assoc(value, f"{flag_name}__mstring", bed_value_list)
        value = assoc(value, f"{flag_name}__boolean", is_present)

    return value
