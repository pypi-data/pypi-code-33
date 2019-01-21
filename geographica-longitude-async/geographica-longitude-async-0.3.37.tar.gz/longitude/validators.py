from collections import Iterable
from copy import copy
from marshmallow.fields import Field
from sanic.exceptions import NotFound
from functools import partial

from longitude.models.sql import SQLCRUDModel
from .exceptions import ValidationError


def validate_obj_attr_uniqueness(
    crudmodel: SQLCRUDModel,
    obj_id: int,
    attr_name: str,
    attr_value
):
    try:
        clashed_obj = crudmodel.get(
            columns=['id'],
            sync=True,
            **{
                attr_name: attr_value
            }
        )

        if clashed_obj and clashed_obj['id'] != obj_id:
            raise ValidationError(
                '{} is already used.'.format(attr_name), attr_name
            )
    except NotFound:
        pass


def validate_obj_attr_existence(model, field_name, pk_val, pk_attr='oid', extra_filters={}):

    kwargs = copy(extra_filters)
    kwargs.update({pk_attr: pk_val})

    many = isinstance(pk_val, Iterable) and not isinstance(pk_val, str)

    obj_count = model.count(sync=True, **kwargs)

    exists = \
        (not many and obj_count == 1) or \
        (many and obj_count == len(pk_val))

    if not exists:
        raise ValidationError('Object does not exists.', field_name)


def validate_max_length(maxl, x):
    if len(x) > maxl:
        raise ValidationError('length cannot be higher than {}'.format(maxl))

    return x


def validate_min_length(minl, x):
    if len(x) < minl:
        raise ValidationError('length cannot be lower than {}'.format(minl))

    return x


def validate_not_blank(x):
    if not x:
        raise ValidationError('cannot be empty')

    return x


def validate_choices_in(choices, x):
    if choices and x not in choices:
        raise ValidationError('value {} not in available choices'.format(x))

    return x


def validate_min_value(minv, x):
    if x < minv:
        raise ValidationError('value must be higher than {}'.format(minv))

    return x


def validate_max_value(maxv, x):
    if x > maxv:
        raise ValidationError('value must be lower than {}'.format(maxv))

    return x


def validate_has_keys(keys, dict):
    missing_keys = set(keys).difference(dict.keys())
    if missing_keys:
        raise ValidationError('the dictionary is missing the following keys: {}'.format(missing_keys))


def validate_elems(elem_type: Field):
    def validate_elems(values):

        if isinstance(values, dict):
            values = values.items()
        else:
            values = enumerate(values)

        errors = {}

        for idx, value in values:
            try:
                elem_type.deserialize(value)
            except ValidationError as e:
                errors[idx] = e.messages

        if errors:
            raise ValidationError(errors)

    return validate_elems


has_keys = lambda keys: partial(validate_has_keys, keys)
max_length = lambda maxl: partial(validate_max_length, maxl)
min_length = lambda minl: partial(validate_min_length, minl)
not_blank = validate_not_blank
choices_in = lambda choices: partial(validate_choices_in, tuple(choices))
min_value = lambda minv: partial(validate_min_value, minv)
max_value = lambda maxv: partial(validate_max_value, maxv)

def combine_validations(*validators):
    def combined_validator(x):
        valid = True

        for validate in validators:
            ret = validate(x)
            valid = valid and (ret is None or ret)

        return valid

    return combined_validator
